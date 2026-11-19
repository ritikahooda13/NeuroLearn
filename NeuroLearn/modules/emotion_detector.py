"""
NeuroLearn - Emotion Detection Module
------------------------------------
Professional-grade real-time facial emotion recognition.

Features:
- MediaPipe Face Detection (robust under varied lighting & pose)
- Vision Transformer for 7-class emotion classification
- Temporal smoothing (moving average over recent frames)
- Confidence thresholding to avoid noisy predictions
- Graceful fallbacks and comprehensive error handling

Author: Ritika (Roll No. 2311078)
Project: NeuroLearn - Adaptive Multimodal Intelligent Tutoring System
"""

import cv2
import numpy as np
from PIL import Image
import torch
from transformers import ViTImageProcessor, ViTForImageClassification
from collections import deque
from typing import Tuple, Dict, Optional, List
import logging
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("NeuroLearn.EmotionDetector")


class EmotionDetector:
    """
    Robust emotion detector designed for real-world tutoring scenarios.
    """

    EMOTION_LABELS = [
        "Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"
    ]

    EDUCATIONAL_STATE = {
        "Happy": "Engaged & Positive",
        "Surprise": "Curious / Interested",
        "Neutral": "Focused / Neutral",
        "Sad": "Confused / Frustrated",
        "Fear": "Anxious / Overwhelmed",
        "Angry": "Frustrated / Stuck",
        "Disgust": "Disengaged"
    }

    # Color mapping for visualization (BGR)
    STATE_COLORS = {
        "Engaged & Positive": (0, 220, 100),
        "Curious / Interested": (0, 200, 255),
        "Focused / Neutral": (200, 200, 50),
        "Confused / Frustrated": (0, 140, 255),
        "Anxious / Overwhelmed": (50, 50, 255),
        "Frustrated / Stuck": (0, 0, 220),
        "Disengaged": (120, 120, 120)
    }

    def __init__(
        self,
        model_name: str = "abhilash88/face-emotion-detection",
        confidence_threshold: float = 0.48,
        smoothing_window: int = 6,
        min_face_size: int = 80
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.confidence_threshold = confidence_threshold
        self.smoothing_window = max(3, smoothing_window)
        self.min_face_size = min_face_size

        self.processor = None
        self.model = None
        self.face_detector = None
        self._emotion_history: deque = deque(maxlen=self.smoothing_window)
        self._last_valid_result: Dict = self._empty_result()

        self._load_models(model_name)

    def _empty_result(self) -> Dict:
        return {
            "face_detected": False,
            "emotion": "Neutral",
            "confidence": 0.0,
            "educational_state": "Focused / Neutral",
            "all_probabilities": {},
            "bbox": None,
            "smoothed": False
        }

    def _load_models(self, model_name: str):
        """Load MediaPipe face detector and Vision Transformer emotion model."""
        # ---- MediaPipe Face Detection ----
        try:
            import mediapipe as mp
            self.mp_face = mp.solutions.face_detection
            self.face_detector = self.mp_face.FaceDetection(
                model_selection=1,          # 1 = full range (better for varied distances)
                min_detection_confidence=0.55
            )
            logger.info("MediaPipe Face Detection loaded successfully.")
        except Exception as e:
            logger.warning(f"MediaPipe failed to load ({e}). Falling back to Haar Cascade.")
            self.face_detector = None
            self.haar = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

        # ---- Vision Transformer Emotion Model ----
        try:
            logger.info(f"Loading emotion model on {self.device} ...")
            self.processor = ViTImageProcessor.from_pretrained(model_name)
            self.model = ViTForImageClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Emotion classification model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            self.processor = None
            self.model = None

    def _detect_faces_mediapipe(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Return list of (x, y, w, h) using MediaPipe."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detector.process(rgb)
        faces = []
        if results.detections:
            h, w, _ = frame.shape
            for det in results.detections:
                bbox = det.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                bw = int(bbox.width * w)
                bh = int(bbox.height * h)
                # Expand a bit for better emotion crop
                x = max(0, x - int(0.05 * bw))
                y = max(0, y - int(0.08 * bh))
                bw = min(w - x, int(bw * 1.15))
                bh = min(h - y, int(bh * 1.15))
                if bw >= self.min_face_size and bh >= self.min_face_size:
                    faces.append((x, y, bw, bh))
        return faces

    def _detect_faces_haar(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Fallback Haar cascade."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = self.haar.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5,
            minSize=(self.min_face_size, self.min_face_size)
        )
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in detections]

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        try:
            if self.face_detector is not None:
                return self._detect_faces_mediapipe(frame)
            return self._detect_faces_haar(frame)
        except Exception as e:
            logger.warning(f"Face detection error: {e}")
            return []

    def predict_emotion(self, face_img: np.ndarray) -> Tuple[str, float, Dict]:
        """Predict emotion from a cropped face image."""
        if self.model is None or self.processor is None:
            return "Neutral", 0.5, {}

        try:
            face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(face_rgb)

            inputs = self.processor(images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

            conf, pred_idx = torch.max(probs, dim=0)
            emotion = self.EMOTION_LABELS[pred_idx.item()]
            confidence = conf.item()
            all_probs = {
                self.EMOTION_LABELS[i]: float(probs[i])
                for i in range(len(self.EMOTION_LABELS))
            }
            return emotion, confidence, all_probs
        except Exception as e:
            logger.warning(f"Emotion prediction failed: {e}")
            return "Neutral", 0.0, {}

    def _smooth_emotion(self, emotion: str, confidence: float) -> Tuple[str, float, bool]:
        """
        Apply temporal smoothing.
        Returns (final_emotion, final_confidence, was_smoothed)
        """
        self._emotion_history.append((emotion, confidence))

        if len(self._emotion_history) < 3:
            return emotion, confidence, False

        # Majority vote weighted by confidence
        scores = {}
        for emo, conf in self._emotion_history:
            scores[emo] = scores.get(emo, 0.0) + conf

        best_emotion = max(scores, key=scores.get)
        avg_conf = scores[best_emotion] / max(1, sum(1 for e, _ in self._emotion_history if e == best_emotion))

        return best_emotion, min(avg_conf, 1.0), True

    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Full pipeline: detect face → predict → smooth → threshold.
        Always returns a valid dictionary (never crashes).
        """
        result = self._empty_result()

        if frame is None or frame.size == 0:
            return result

        try:
            faces = self.detect_faces(frame)
            if not faces:
                # Keep last valid result for a short time (stability)
                if self._last_valid_result["face_detected"]:
                    return self._last_valid_result
                return result

            # Largest face
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            face_img = frame[y:y + h, x:x + w]

            if face_img.size == 0:
                return result

            emotion, conf, probs = self.predict_emotion(face_img)

            # Confidence threshold
            if conf < self.confidence_threshold:
                emotion = "Neutral"
                # still keep original conf for transparency

            # Temporal smoothing
            emotion, conf, smoothed = self._smooth_emotion(emotion, conf)

            result.update({
                "face_detected": True,
                "emotion": emotion,
                "confidence": round(conf, 3),
                "educational_state": self.EDUCATIONAL_STATE.get(emotion, "Focused / Neutral"),
                "all_probabilities": probs,
                "bbox": (x, y, w, h),
                "smoothed": smoothed
            })

            self._last_valid_result = result.copy()
            return result

        except Exception as e:
            logger.error(f"process_frame failed: {e}")
            return self._last_valid_result if self._last_valid_result["face_detected"] else result

    def draw_overlay(self, frame: np.ndarray, result: Dict) -> np.ndarray:
        """Draw professional bounding box + labels on the frame."""
        try:
            display = frame.copy()
            if not result.get("face_detected") or result.get("bbox") is None:
                cv2.putText(
                    display, "No face detected", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 220), 2
                )
                return display

            x, y, w, h = result["bbox"]
            state = result["educational_state"]
            emotion = result["emotion"]
            conf = result["confidence"]
            color = self.STATE_COLORS.get(state, (200, 200, 200))

            # Bounding box
            cv2.rectangle(display, (x, y), (x + w, y + h), color, 2)

            # Labels with background for readability
            label1 = f"{emotion} ({conf:.0%})"
            label2 = state

            (tw1, th1), _ = cv2.getTextSize(label1, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
            (tw2, th2), _ = cv2.getTextSize(label2, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)

            cv2.rectangle(display, (x, y - th1 - th2 - 16), (x + max(tw1, tw2) + 12, y), color, -1)
            cv2.putText(display, label1, (x + 5, y - th2 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            cv2.putText(display, label2, (x + 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

            return display
        except Exception:
            return frame

    def reset_history(self):
        """Clear smoothing history (useful when switching users)."""
        self._emotion_history.clear()
        self._last_valid_result = self._empty_result()
