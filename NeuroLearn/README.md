# 🧠 NeuroLearn
**Adaptive Multimodal Intelligent Tutoring System**

Final Year Major Project – B.Tech CSE (AIML)  
**UIET, Maharshi Dayanand University (MDU)**  
**Student:** Ritika (Roll No. 2311078)  
**Guide:** Dr. Munisha

This project is a working tutoring system that looks at the student’s facial expressions, keeps track of their knowledge, and changes its teaching style based on both.

---

## ✨ Complete Feature List

| Module | Technology | Status |
|--------|------------|--------|
| Real-time Emotion Recognition | MediaPipe Face Detection + Vision Transformer | ✅ |
| Temporal Emotion Smoothing | Moving-window majority vote + confidence | ✅ |
| Educational State Mapping | Emotion → Pedagogy rules | ✅ |
| Hybrid Knowledge Tracing | BKT + difficulty-aware learning + forgetting curve | ✅ |
| Adaptive LLM Tutor | Emotion + Mastery conditioned prompting | ✅ |
| Retrieval-Augmented Generation | PDF/Notes → Chunk → Embed → Retrieve | ✅ |
| Text-to-Speech | edge-tts (Neural voices) | ✅ |
| Student Model Persistence | JSON based long-term tracking | ✅ |
| Interactive Dashboard | Streamlit + Plotly mastery charts | ✅ |
| Offline Fallback Mode | Fully functional without API key | ✅ |
| Robust Error Handling | Graceful degradation throughout | ✅ |

---

## 🏗️ Project Structure

```
NeuroLearn/
├── app.py                      # Main Streamlit application
├── requirements.txt
├── README.md
├── modules/
│   ├── emotion_detector.py     # MediaPipe + ViT + temporal smoothing
│   ├── knowledge_tracer.py     # Hybrid BKT + forgetting curve
│   ├── tutor.py                # Emotion-aware adaptive LLM tutor
│   ├── rag.py                  # Document RAG (PDF support)
│   └── speech.py               # High-quality TTS
├── data/                       # Runtime student model + RAG store
├── docs/                       # Report, Synopsis, Presentation
├── models/
└── assets/
```

---

## 🚀 Quick Start

```bash
cd NeuroLearn
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

**Optional but Recommended:**
- Get free API key from [console.groq.com](https://console.groq.com)
- Paste it in the sidebar for full LLM intelligence

---

## 📖 How to Demonstrate (Viva / Demo Flow)

1. **Emotion Adaptation**
   - Turn on webcam or simulate “Confused / Frustrated”
   - Ask a hard question → observe simplified, supportive response
   - Change to “Engaged & Positive” → response becomes deeper & challenging

2. **Knowledge Tracing**
   - Click “Quiz Me” → answer → click “Mark Correct”
   - Watch mastery bar chart update in real time

3. **RAG Grounding**
   - Upload any PDF notes / textbook chapter
   - Ask questions from that material → answers are grounded + cited

4. **TTS**
   - Enable “Auto Text-to-Speech”
   - Tutor replies are spoken in natural neural voice

---

## 🧠 Technical Highlights (for Report & Viva)

- **Perception**: Vision Transformer fine-tuned for 7-class emotion recognition
- **Student Modeling**: Classic BKT enhanced with difficulty-modulated learning rate + persistent concept-level mastery
- **Pedagogical Adaptation**: Explicit mapping from affective state → teaching strategy (scaffolding, cognitive load theory inspired)
- **Grounded Generation**: Lightweight RAG using MiniLM embeddings + cosine retrieval
- **Multimodal Output**: Text + high-quality neural TTS
- **Fully modular & extensible** design

---

## 📄 Documentation Included

- `docs/synopsis.md` — Project Synopsis
- `docs/project_report.md` — Detailed Project Report outline + content

---

## 🔮 Future Enhancements

- YOLOv8 / MediaPipe face detection
- Full Transformer-based Knowledge Tracing (AKT / SAINT+)
- Whisper speech-to-text
- Multi-student classroom mode
- Edge deployment (Jetson / Raspberry Pi)
- LoRA fine-tuned educational LLM

---

**NeuroLearn** — A tutor that understands both what you know and how you feel.
