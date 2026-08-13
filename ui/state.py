# ui/state.py
"""
Single place that owns every st.session_state key EduRAG uses, so screens
never scatter ad-hoc `if "x" not in st.session_state` checks.
"""
import streamlit as st

NAV_ITEMS = [
    ("home", "🏠", "Home"),
    ("tutor", "🤖", "AI Tutor"),
    ("practice", "🧠", "Practice"),
    ("quiz", "📝", "Quiz"),
    ("progress", "📊", "Progress"),
    ("library", "📚", "NCERT Library"),
]

# The only subject/class actually indexed in faiss_index/ right now.
# Kept as constants (not hardcoded in every screen) so adding a second
# subject later is a one-line change once more PDFs are ingested.
DEFAULT_SUBJECT = "Physics"
DEFAULT_CLASS = "Class 12"


def init_session_state():
    defaults = {
        "view": "home",
        "messages": [],
        "conversation_context": "",
        "user_language": "en",
        "selected_subject": DEFAULT_SUBJECT,
        "selected_class": DEFAULT_CLASS,
        "selected_chapter": None,
        "pending_prompt": None,
        "practice_state": None,
        "quiz_state": None,
        "show_debug": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(view_key: str):
    st.session_state.view = view_key
