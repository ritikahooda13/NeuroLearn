# NeuroLearn 🧠

**Adaptive Multimodal Intelligent Tutoring System using Deep Learning and Generative AI**



---

## Overview

NeuroLearn is an adaptive AI tutor that:

- Detects the student's **emotion** from the webcam (or simulation)
- Tracks **concept-level knowledge** with a hybrid Knowledge Tracing model
- Changes its **teaching style** based on emotion + knowledge state
- Answers using **RAG** over uploaded PDFs/notes
- Supports **Text-to-Speech**

Unlike normal chatbots, it adapts tone and depth when the student is confused, frustrated, or engaged.

---

## Features

| Feature | Description |
|--------|-------------|
| Emotion Sensing | MediaPipe + Vision Transformer, temporal smoothing |
| Knowledge Tracing | Hybrid BKT with forgetting curve |
| Adaptive Tutor | Emotion + knowledge aware LLM (Groq) |
| RAG | Upload PDFs/notes for grounded answers |
| TTS | Neural text-to-speech (edge-tts) |
| Dashboard | Streamlit UI with mastery map & chat |

---

## How to Run

```bash
cd NeuroLearn
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py