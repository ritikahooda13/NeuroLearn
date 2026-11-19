"""
NeuroLearn - Knowledge Tracing Module
-------------------------------------
Hybrid Bayesian Knowledge Tracing with difficulty awareness,
temporal forgetting, and persistent student modeling.

Designed for reliability and interpretability in real tutoring scenarios.

Author: Ritika (Roll No. 2311078)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("NeuroLearn.KnowledgeTracer")


class KnowledgeTracer:
    """
    Practical yet principled knowledge tracer.
    - Classic BKT observation & learning updates
    - Difficulty-modulated learning rate
    - Simple exponential forgetting over time
    - Robust persistence and error handling
    """

    def __init__(
        self,
        concepts: Optional[List[str]] = None,
        save_path: str = "data/student_model.json",
        p_init: float = 0.22,
        p_learn: float = 0.28,
        p_guess: float = 0.18,
        p_slip: float = 0.12,
        forgetting_rate: float = 0.015          # per day
    ):
        self.save_path = save_path
        self.p_init = p_init
        self.p_learn = p_learn
        self.p_guess = p_guess
        self.p_slip = p_slip
        self.forgetting_rate = forgetting_rate

        self.concepts = concepts or [
            "Variables & Data Types",
            "Control Flow",
            "Functions",
            "Object Oriented Programming",
            "Data Structures - Arrays",
            "Data Structures - Linked Lists",
            "Sorting Algorithms",
            "Searching Algorithms",
            "Recursion",
            "Dynamic Programming",
            "Neural Networks Basics",
            "Backpropagation",
            "CNNs",
            "Transformers",
            "Attention Mechanism"
        ]

        self.mastery: Dict[str, float] = {c: self.p_init for c in self.concepts}
        self.attempts: Dict[str, int] = {c: 0 for c in self.concepts}
        self.correct: Dict[str, int] = {c: 0 for c in self.concepts}
        self.last_practiced: Dict[str, Optional[str]] = {c: None for c in self.concepts}
        self.history: List[Dict] = []

        self._load()

    def _load(self):
        """Load previously saved student model if available."""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.mastery = data.get("mastery", self.mastery)
                self.attempts = data.get("attempts", self.attempts)
                self.correct = data.get("correct", self.correct)
                self.last_practiced = data.get("last_practiced", self.last_practiced)
                self.history = data.get("history", [])[-400:]  # keep recent
                # Apply forgetting since last save
                self._apply_forgetting()
                logger.info("Student model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load student model: {e}. Starting fresh.")

    def save(self):
        """Persist current student state."""
        try:
            os.makedirs(os.path.dirname(self.save_path) or ".", exist_ok=True)
            data = {
                "mastery": self.mastery,
                "attempts": self.attempts,
                "correct": self.correct,
                "last_practiced": self.last_practiced,
                "history": self.history[-400:],
                "updated_at": datetime.now().isoformat()
            }
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save student model: {e}")

    def _apply_forgetting(self):
        """Simple exponential forgetting based on days since last practice."""
        now = datetime.now()
        for concept in self.concepts:
            last = self.last_practiced.get(concept)
            if last is None:
                continue
            try:
                last_dt = datetime.fromisoformat(last)
                days = max(0.0, (now - last_dt).total_seconds() / 86400.0)
                if days > 0.5:
                    decay = np.exp(-self.forgetting_rate * days)
                    # Move mastery toward prior
                    self.mastery[concept] = (
                        self.p_init + (self.mastery[concept] - self.p_init) * decay
                    )
                    self.mastery[concept] = float(np.clip(self.mastery[concept], 0.02, 0.98))
            except Exception:
                continue

    def update(self, concept: str, is_correct: bool, difficulty: float = 0.5) -> float:
        """
        Update knowledge state after an interaction.
        difficulty: 0.0 (very easy) → 1.0 (very hard)
        Returns new mastery.
        """
        if concept not in self.mastery:
            self.mastery[concept] = self.p_init
            self.attempts[concept] = 0
            self.correct[concept] = 0
            self.last_practiced[concept] = None

        # Apply forgetting first
        self._apply_forgetting()

        p_know = float(self.mastery[concept])
        difficulty = float(np.clip(difficulty, 0.0, 1.0))

        try:
            if is_correct:
                p_correct = p_know * (1 - self.p_slip) + (1 - p_know) * self.p_guess
                p_know = (p_know * (1 - self.p_slip)) / max(p_correct, 1e-9)
            else:
                p_incorrect = p_know * self.p_slip + (1 - p_know) * (1 - self.p_guess)
                p_know = (p_know * self.p_slip) / max(p_incorrect, 1e-9)

            # Difficulty-aware learning rate (easier items → slightly higher learn chance)
            learn_rate = self.p_learn * (1.0 + 0.35 * (1.0 - difficulty))
            new_mastery = p_know + (1 - p_know) * learn_rate
            new_mastery = float(np.clip(new_mastery, 0.02, 0.98))

            self.mastery[concept] = new_mastery
            self.attempts[concept] += 1
            if is_correct:
                self.correct[concept] += 1
            self.last_practiced[concept] = datetime.now().isoformat()

            self.history.append({
                "concept": concept,
                "correct": bool(is_correct),
                "difficulty": difficulty,
                "mastery_after": new_mastery,
                "timestamp": datetime.now().isoformat()
            })

            self.save()
            return new_mastery

        except Exception as e:
            logger.error(f"Update failed for {concept}: {e}")
            return self.mastery.get(concept, self.p_init)

    def get_mastery(self, concept: Optional[str] = None) -> Dict[str, float]:
        self._apply_forgetting()
        if concept:
            return {concept: self.mastery.get(concept, self.p_init)}
        return dict(self.mastery)

    def get_weak_concepts(self, top_k: int = 3) -> List[Tuple[str, float]]:
        self._apply_forgetting()
        sorted_c = sorted(self.mastery.items(), key=lambda x: x[1])
        return sorted_c[:top_k]

    def get_strong_concepts(self, top_k: int = 3) -> List[Tuple[str, float]]:
        self._apply_forgetting()
        sorted_c = sorted(self.mastery.items(), key=lambda x: x[1], reverse=True)
        return sorted_c[:top_k]

    def recommend_next_concept(self) -> str:
        """Soft selection biased toward weaker concepts."""
        weak = self.get_weak_concepts(6)
        if not weak:
            return self.concepts[0]
        scores = np.array([1.05 - m for _, m in weak])
        probs = scores / scores.sum()
        idx = int(np.random.choice(len(weak), p=probs))
        return weak[idx][0]

    def get_student_summary(self) -> Dict:
        self._apply_forgetting()
        vals = list(self.mastery.values())
        total_attempts = sum(self.attempts.values())
        total_correct = sum(self.correct.values())
        return {
            "average_mastery": float(np.mean(vals)) if vals else 0.0,
            "total_attempts": total_attempts,
            "overall_accuracy": (total_correct / total_attempts) if total_attempts > 0 else 0.0,
            "weak_concepts": self.get_weak_concepts(3),
            "strong_concepts": self.get_strong_concepts(3),
            "num_concepts_tracked": len(self.concepts)
        }

    def reset(self):
        """Reset all student data."""
        self.mastery = {c: self.p_init for c in self.concepts}
        self.attempts = {c: 0 for c in self.concepts}
        self.correct = {c: 0 for c in self.concepts}
        self.last_practiced = {c: None for c in self.concepts}
        self.history = []
        self.save()
        logger.info("Student model reset.")
