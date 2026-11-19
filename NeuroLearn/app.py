"""
NeuroLearn - Adaptive Multimodal Intelligent Tutoring System
===========================================================
A production-quality prototype that combines:
• Real-time emotion recognition (MediaPipe + Vision Transformer)
• Hybrid Knowledge Tracing with forgetting
• Emotion- & mastery-aware LLM tutoring
• Retrieval-Augmented Generation over course materials
• Neural Text-to-Speech

Author : Ritika (Roll No. 2311078)
College: UIET, Maharshi Dayanand University (MDU)
Guide  : Dr. Munisha
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import plotly.express as px
import pandas as pd
import os
import tempfile
from datetime import datetime

# Local modules
from modules.emotion_detector import EmotionDetector
from modules.knowledge_tracer import KnowledgeTracer
from modules.tutor import AdaptiveTutor
from modules.rag import DocumentRAG
from modules.speech import SpeechHandler, get_available_voices

# ------------------------- Page Config -------------------------
st.set_page_config(
    page_title="NeuroLearn | Adaptive AI Tutor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------- Custom CSS -------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        color: #999;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------- Session State Initialization -------------------------
@st.cache_resource(show_spinner=False)
def load_emotion_detector():
    try:
        return EmotionDetector(
            confidence_threshold=0.48,
            smoothing_window=6
        )
    except Exception as e:
        st.error(f"Failed to initialize emotion detector: {e}")
        return None

if "emotion_detector" not in st.session_state:
    with st.spinner("Loading emotion recognition models (MediaPipe + ViT)..."):
        st.session_state.emotion_detector = load_emotion_detector()

if "knowledge_tracer" not in st.session_state:
    st.session_state.knowledge_tracer = KnowledgeTracer()

if "tutor" not in st.session_state:
    st.session_state.tutor = AdaptiveTutor()

if "rag" not in st.session_state:
    st.session_state.rag = DocumentRAG()

if "speech" not in st.session_state:
    st.session_state.speech = SpeechHandler()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_emotion" not in st.session_state:
    st.session_state.current_emotion = {
        "emotion": "Neutral",
        "educational_state": "Focused / Neutral",
        "confidence": 0.0,
        "face_detected": False
    }

if "last_audio_path" not in st.session_state:
    st.session_state.last_audio_path = None


# ------------------------- Sidebar -------------------------
with st.sidebar:
    st.markdown("## 🧠 NeuroLearn")
    st.caption("Advanced Multimodal Adaptive Tutor")
    st.divider()

    # ---- Emotion ----
    st.subheader("📷 Emotion Sensing")
    camera_mode = st.toggle("Enable Webcam", value=False)

    if not camera_mode:
        manual_emotion = st.selectbox(
            "Simulate Student State",
            [
                "Engaged & Positive",
                "Curious / Interested",
                "Focused / Neutral",
                "Confused / Frustrated",
                "Anxious / Overwhelmed",
                "Frustrated / Stuck",
                "Disengaged"
            ],
            index=2
        )
        st.session_state.current_emotion = {
            "emotion": manual_emotion.split(" ")[0],
            "educational_state": manual_emotion,
            "confidence": 0.92,
            "face_detected": True
        }

    st.divider()

    # ---- RAG / Documents ----
    st.subheader("📚 Course Materials (RAG)")
    uploaded_files = st.file_uploader(
        "Upload PDFs / Notes",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name
            with st.spinner(f"Indexing {uploaded.name}..."):
                n_chunks = st.session_state.rag.add_document(tmp_path, source_name=uploaded.name)
            st.success(f"✅ {uploaded.name} → {n_chunks} chunks")
            os.unlink(tmp_path)

    rag_status = st.session_state.rag.status()
    if rag_status["num_chunks"] > 0:
        st.info(f"📄 {rag_status['num_sources']} documents | {rag_status['num_chunks']} chunks")
        if st.button("🗑️ Clear All Documents"):
            st.session_state.rag.clear()
            st.rerun()

    st.divider()

    # ---- Student Model ----
    st.subheader("📊 Student Model")
    summary = st.session_state.knowledge_tracer.get_student_summary()
    c1, c2 = st.columns(2)
    c1.metric("Mastery", f"{summary['average_mastery']:.0%}")
    c2.metric("Attempts", summary['total_attempts'])

    if st.button("🔄 Reset Student Model"):
        st.session_state.knowledge_tracer = KnowledgeTracer()
        st.success("Reset done!")
        st.rerun()

    st.divider()

    # ---- Settings ----
    st.subheader("⚙️ Settings")
    st.divider()

    # ---- Settings ----
    st.subheader("⚙️ Settings")

    # Permanent API key storage
    KEY_FILE = "data/api_key.txt"
    saved_key = ""
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r") as f:
                saved_key = f.read().strip()
        except Exception:
            saved_key = ""

    api_key = st.text_input(
        "Groq / OpenAI API Key",
        value=saved_key,
        type="password",
        help="Free key from console.groq.com — saved permanently after first entry"
    )

    if api_key:
        try:
            os.makedirs("data", exist_ok=True)
            with open(KEY_FILE, "w") as f:
                f.write(api_key)
        except Exception:
            pass
        st.session_state.tutor = AdaptiveTutor(api_key=api_key)
        st.success("LLM Connected ✓ (Key saved permanently)")
    elif saved_key:
        st.session_state.tutor = AdaptiveTutor(api_key=saved_key)
        st.success("LLM Connected ✓ (Loaded saved key)")

    voice_options = get_available_voices()
    selected_voice = st.selectbox("TTS Voice", list(voice_options.keys()))
    st.session_state.speech.set_voice(voice_options[selected_voice])

    enable_tts = st.toggle("Auto Text-to-Speech", value=False)

    st.caption("B.Tech CSE-AIML Final Year Project")


# ------------------------- Main Header -------------------------
st.markdown('<p class="main-header">NeuroLearn</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Real-time Emotion-Aware • Knowledge-Adaptive • RAG-Grounded AI Tutor</p>', unsafe_allow_html=True)

# Top status bar
s1, s2, s3, s4 = st.columns(4)
s1.metric("Current State", st.session_state.current_emotion["educational_state"].split(" ")[0])
s2.metric("Confidence", f"{st.session_state.current_emotion.get('confidence', 0):.0%}")
weak = summary.get("weak_concepts", [])
s3.metric("Weakest Topic", weak[0][0][:18] + "…" if weak else "—")
s4.metric("Docs Loaded", rag_status["num_sources"])

st.divider()

# ------------------------- Main Layout -------------------------
left, right = st.columns([1, 1.35])

with left:
    st.subheader("🎥 Perception & Knowledge")

    # Camera / Emotion
    if camera_mode:
        img_file = st.camera_input("Position your face clearly in the frame", key="cam")
        if img_file is not None:
            try:
                image = Image.open(img_file)
                frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                if st.session_state.emotion_detector is not None:
                    result = st.session_state.emotion_detector.process_frame(frame)
                    st.session_state.current_emotion = result

                    annotated = st.session_state.emotion_detector.draw_overlay(frame.copy(), result)
                    st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_container_width=True)

                    if result["face_detected"]:
                        conf_pct = f"{result['confidence']:.0%}"
                        smooth_tag = " (smoothed)" if result.get("smoothed") else ""
                        st.success(f"**{result['emotion']}** ({conf_pct}) → {result['educational_state']}{smooth_tag}")
                    else:
                        st.warning("No face detected. Please look at the camera.")
                else:
                    st.error("Emotion detector not available.")
            except Exception as e:
                st.error(f"Could not process camera frame: {e}")
    else:
        st.info("Webcam off — using simulated emotional state from the sidebar.")
        st.markdown(f"### {st.session_state.current_emotion.get('educational_state', 'Focused / Neutral')}")

    # Mastery Chart
    st.markdown("##### Knowledge Mastery Map")
    mastery = st.session_state.knowledge_tracer.get_mastery()
    df = pd.DataFrame({"Concept": list(mastery.keys()), "Mastery": list(mastery.values())})
    fig = px.bar(df, x="Mastery", y="Concept", orientation="h",
                 color="Mastery", color_continuous_scale="Tealgrn", range_x=[0, 1])
    fig.update_layout(height=380, margin=dict(l=5, r=5, t=20, b=5),
                      coloraxis_showscale=False, yaxis=dict(tickfont=dict(size=11)))
    st.plotly_chart(fig, use_container_width=True)


with right:
    st.subheader("💬 Adaptive Tutor")

    # Chat history
    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("audio"):
                    st.audio(msg["audio"])

    # Input
    if prompt := st.chat_input("Ask a question, request explanation, or say 'quiz me'..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        # RAG retrieval
        rag_context = ""
        if st.session_state.rag.status()["num_chunks"] > 0:
            rag_context = st.session_state.rag.get_context(prompt, top_k=4)

        with st.spinner("🧠 Adapting to your state & generating response..."):
            response = st.session_state.tutor.generate_response(
                user_message=prompt,
                emotion_state=st.session_state.current_emotion["educational_state"],
                knowledge_summary=summary,
                current_concept=weak[0][0] if weak else None,
                rag_context=rag_context if rag_context else None
            )

        # Optional TTS
        audio_path = None
        if enable_tts:
            with st.spinner("🔊 Generating speech..."):
                audio_path = st.session_state.speech.text_to_speech(response)

        msg = {"role": "assistant", "content": response}
        if audio_path:
            msg["audio"] = audio_path
        st.session_state.messages.append(msg)
        st.rerun()

    # Quick Actions
    st.markdown("**Quick Actions**")
    a1, a2, a3, a4 = st.columns(4)

    with a1:
        if st.button("🎯 Next Topic", use_container_width=True):
            topic = st.session_state.knowledge_tracer.recommend_next_concept()
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Based on your mastery profile, I recommend focusing on **{topic}** next.\n\nShall I explain it step-by-step or give you a diagnostic question first?"
            })
            st.rerun()

    with a2:
        if st.button("📝 Quiz Me", use_container_width=True):
            concept = weak[0][0] if weak else "Transformers"
            mastery_val = weak[0][1] if weak else 0.5
            q = st.session_state.tutor.generate_quiz_question(
                concept, mastery_val, st.session_state.current_emotion["educational_state"]
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**Adaptive Quiz** ({q['difficulty']})\n\n**Concept:** {q['concept']}\n\n{q['question']}\n\nType your answer below. I'll evaluate and update your knowledge model."
            })
            st.rerun()

    with a3:
        if st.button("✅ Mark Correct", use_container_width=True):
            concept = weak[0][0] if weak else list(mastery.keys())[0]
            new_m = st.session_state.knowledge_tracer.update(concept, is_correct=True, difficulty=0.5)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Great job! Updated mastery for **{concept}** → now **{new_m:.0%}**.\n\nKeep going!"
            })
            st.rerun()

    with a4:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.tutor.reset_conversation()
            st.rerun()


# ------------------------- Footer -------------------------
st.divider()
st.caption("NeuroLearn v2.0 • Emotion (ViT) + Hybrid Knowledge Tracing + RAG + Adaptive LLM + TTS • B.Tech CSE-AIML Major Project")
