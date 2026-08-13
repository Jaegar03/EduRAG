# streamlit_app_multilingual.py
"""
EduRAG application shell. All RAG/backend logic lives in
backend_multimodal.py (unchanged) and is orchestrated from ui/rag.py; this
file only wires up page config, global theme, session state, sidebar
navigation, and dispatches to the active screen.
"""
import streamlit as st

from ui.home import render_home
from ui.library import render_library
from ui.practice import render_practice
from ui.profile import render_profile
from ui.progress_view import render_progress
from ui.quiz import render_quiz
from ui.sidebar import render_sidebar
from ui.state import init_session_state
from ui.theme import inject_theme
from ui.tutor import render_ai_tutor

st.set_page_config(
    page_title="EduRAG",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()
init_session_state()
render_sidebar()

VIEWS = {
    "home": render_home,
    "tutor": render_ai_tutor,
    "practice": render_practice,
    "quiz": render_quiz,
    "progress": render_progress,
    "library": render_library,
    "profile": render_profile,
}

view_fn = VIEWS.get(st.session_state.view, render_home)
view_fn()
