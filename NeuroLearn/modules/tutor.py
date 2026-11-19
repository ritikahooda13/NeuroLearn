"""
NeuroLearn - Adaptive LLM Tutor
Emotion-aware + Knowledge-state-aware prompting.
Supports Groq / OpenAI API + intelligent fallback.
"""

import os
from typing import Dict, List, Optional


class AdaptiveTutor:
    """
    Emotion + Knowledge aware Intelligent Tutor.
    """

    SYSTEM_PROMPT = """You are NeuroLearn, an advanced, empathetic, and highly adaptive AI tutor specializing in Computer Science, Artificial Intelligence and Machine Learning.

Your core principles:
1. Always adapt your teaching style, depth, and tone based on the student's current emotional/cognitive state and knowledge mastery.
2. Never dump the full answer immediately. Use scaffolding: guide step-by-step.
3. Be encouraging when the student is frustrated or confused. Be challenging when they are engaged.
4. Use simple analogies and real-world examples.
5. Keep responses clear and well-structured. Do not make them too long unless asked.

Current Student State will be provided. Strictly follow the adaptation rules based on it.
"""

    ADAPTATION_RULES = {
        "Engaged & Positive": {
            "tone": "enthusiastic and slightly challenging",
            "depth": "can go deeper, introduce advanced insights",
            "style": "ask thought-provoking questions, encourage exploration"
        },
        "Curious / Interested": {
            "tone": "excited and exploratory",
            "depth": "provide rich explanations and connections",
            "style": "use analogies, link to related concepts"
        },
        "Focused / Neutral": {
            "tone": "clear, professional, structured",
            "depth": "standard clear explanation",
            "style": "step-by-step, well-organized"
        },
        "Confused / Frustrated": {
            "tone": "patient, supportive, calming",
            "depth": "simplify significantly, break into tiny steps",
            "style": "use simpler language, more examples, check understanding frequently"
        },
        "Anxious / Overwhelmed": {
            "tone": "very gentle, reassuring, confidence-building",
            "depth": "minimal new information, focus on one small idea",
            "style": "short sentences, lots of encouragement"
        },
        "Frustrated / Stuck": {
            "tone": "empathetic and motivating",
            "depth": "go back to fundamentals",
            "style": "identify the exact misconception, give a different angle"
        },
        "Disengaged": {
            "tone": "energetic, interesting, curiosity-sparking",
            "depth": "make it relevant and exciting",
            "style": "use surprising facts and short interactive questions"
        }
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.conversation_history: List[Dict] = []
        self.use_api = False
        self.last_error = None
        self.provider = None
        self.client = None

        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                self.provider = "groq"
                self.use_api = True
            except Exception:
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                    self.provider = "openai"
                    self.use_api = True
                except Exception as e:
                    self.use_api = False
                    self.last_error = str(e)

    def _build_context(self, emotion_state: str, knowledge_summary: Dict, concept: str = None) -> str:
        rules = self.ADAPTATION_RULES.get(emotion_state, self.ADAPTATION_RULES["Focused / Neutral"])

        weak = knowledge_summary.get("weak_concepts", [])
        strong = knowledge_summary.get("strong_concepts", [])
        avg = knowledge_summary.get("average_mastery", 0.5)

        context = f"""
=== CURRENT STUDENT STATE ===
Emotional / Cognitive State: {emotion_state}
Recommended Tone: {rules['tone']}
Recommended Depth: {rules['depth']}
Recommended Style: {rules['style']}

Knowledge Profile:
- Average Mastery: {avg:.1%}
- Weak Concepts: {', '.join([f'{c} ({m:.0%})' for c, m in weak]) if weak else 'None yet'}
- Strong Concepts: {', '.join([f'{c} ({m:.0%})' for c, m in strong]) if strong else 'None yet'}
"""
        if concept:
            context += f"- Currently focusing on: {concept}\n"

        context += "=== END STATE ===\n"
        return context

    def generate_response(
        self,
        user_message: str,
        emotion_state: str = "Focused / Neutral",
        knowledge_summary: Dict = None,
        current_concept: str = None,
        rag_context: str = None
    ) -> str:
        knowledge_summary = knowledge_summary or {}
        state_context = self._build_context(emotion_state, knowledge_summary, current_concept)

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "system", "content": state_context}
        ]

        if rag_context:
            messages.append({
                "role": "system",
                "content": "Use the following course material to ground your answer:\n\n" + rag_context
            })

        for turn in self.conversation_history[-6:]:
            messages.append(turn)

        messages.append({"role": "user", "content": user_message})

        if self.use_api and self.client:
            models_to_try = [
                self.model,
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "openai/gpt-oss-20b",
            ]
            reply = None
            last_err = None

            for m in models_to_try:
                try:
                    response = self.client.chat.completions.create(
                        model=m,
                        messages=messages,
                        temperature=0.65,
                        max_tokens=900
                    )
                    reply = response.choices[0].message.content.strip()
                    if reply:
                        break
                except Exception as e:
                    last_err = str(e)
                    continue

            if not reply:
                self.last_error = last_err
                fallback = self._fallback_response(user_message, emotion_state, current_concept)
                reply = f"⚠️ API Error: {last_err}\n\n{fallback}"
        else:
            reply = self._fallback_response(user_message, emotion_state, current_concept)

        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": reply})

        return reply

    def _fallback_response(self, user_message: str, emotion_state: str, concept: str = None) -> str:
        msg = user_message.lower()
        base = f"[NeuroLearn Adaptive Mode | State: {emotion_state}]\n\n"

        if any(x in emotion_state for x in ["Confused", "Frustrated", "Anxious", "Stuck"]):
            if "explain" in msg or "what is" in msg or "how" in msg:
                return base + (
                    "I can see this might feel a bit tricky right now — that's completely okay.\n\n"
                    f"You asked: **{user_message}**\n\n"
                    "Let's break it into very small pieces:\n\n"
                    "1. First, the core idea in one simple sentence.\n"
                    "2. Then a real-life example.\n"
                    "3. Finally one tiny practice question.\n\n"
                    "Would you like me to start with a simple real-life example?"
                )
            return base + (
                "No worries, we can slow down.\n\n"
                "Tell me which part feels most confusing and I'll explain only that part "
                "in the simplest way possible."
            )

        if any(x in emotion_state for x in ["Engaged", "Curious", "Positive"]):
            return base + (
                f"Great energy! Let's explore this properly.\n\n"
                f"**{user_message}**\n\n"
                "Here's a clear explanation:\n\n"
                "• Core concept\n"
                "• Why it matters\n"
                "• How it works (step-by-step)\n"
                "• One interesting advanced point\n\n"
                "Want me to go deeper or give you a challenge question?"
            )

        if "quiz" in msg or "question" in msg or "test" in msg:
            return base + (
                "Sure! Here's a quick question for you:\n\n"
                "**What is the main difference between a list and a tuple in Python?**\n\n"
                "Take your time and answer in your own words. "
                "After you answer, click **Mark Correct** or tell me if you want the solution."
            )

        if "explain" in msg or "what is" in msg:
            return base + (
                f"Here's a clear explanation of **{user_message}**:\n\n"
                "1. **Core Idea**: ...\n"
                "2. **Why it matters**: ...\n"
                "3. **How it works (step-by-step)**: ...\n\n"
                "Want me to go deeper, give an analogy, or quiz you on this?"
            )

        return base + (
            f"Got it! You said: **{user_message}**\n\n"
            "I can explain this topic, give examples, or quiz you. "
            "Just tell me what you prefer (or click the Quick Action buttons)."
        )

    def clear_history(self):
        self.conversation_history = []