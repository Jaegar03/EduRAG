# 🎓 EduRAG

AI-powered NCERT learning companion, built with Retrieval-Augmented Generation (RAG). Ask questions in natural language and get answers grounded in the indexed NCERT textbook content, with citations back to the source chapter and page — plus AI-generated practice sets and quizzes, all in a single Streamlit app.

## Features

- **AI Tutor** — conversational Q&A over NCERT textbooks with source citations, multilingual text/voice input, image upload, and text-to-speech responses.
- **Practice Arena** — AI-generated multiple-choice questions grounded in the actual textbook content, answered one at a time with explanations.
- **Quiz Center** — timed quizzes with a question navigator and scoring.
- **Progress dashboard** — streaks, accuracy, subject performance, and a learning-activity heatmap, computed from real local usage data (not placeholders).
- **NCERT Library** — browse indexed chapters, auto-extracted from the source PDFs.

## Architecture

```
streamlit_app_multilingual.py   Entry point / app shell (page config, theme, navigation)
ui/                              Screens and UI components
  ├─ home.py, tutor.py, practice.py, quiz.py,
  │  progress_view.py, library.py, profile.py
  ├─ components.py, sidebar.py, theme.py, state.py
  └─ rag.py                      Orchestrates calls into backend_multimodal.py
backend_multimodal.py            RAG pipeline: FAISS store, Gemini LLM, hybrid
                                  search, voice/image/TTS, question generation
ingest.py                        Builds the FAISS index from PDFs in data/
progress_store.py                Local JSON persistence for practice/quiz
                                  history and activity stats
data/                             Source NCERT textbook PDFs
```

## Setup

**1. Clone and create a virtual environment**

```bash
git clone https://github.com/Jaegar03/EduRAG.git
cd EduRAG
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Add your Gemini API key**

Create a `.env` file in the project root (never commit this file):

```
GOOGLE_API_KEY="your_key_here"
```

Get a key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).

**4. Build the vector index**

`data/` already contains the NCERT Physics (Class 12, Part 1) textbook. Build the FAISS index:

```bash
python ingest.py
```

This creates a local `faiss_index/` folder (gitignored — rebuild it any time from `data/`).

**5. Run the app**

```bash
streamlit run streamlit_app_multilingual.py
```

## Notes

- Voice input uses `sounddevice` for microphone capture (no PyAudio/compiler toolchain required).
- Currently indexed content: NCERT Physics, Class 12, Part 1 (8 chapters). Add more subjects by dropping additional PDFs into `data/` and re-running `ingest.py`.
- Practice/Quiz questions are generated live by Gemini from the retrieved textbook context — not hardcoded.
