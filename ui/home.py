# ui/home.py
from datetime import datetime

import streamlit as st

import progress_store
from ui.components import quick_action, render_hero, render_progress_bar
from ui.library import get_library_chapters
from ui.state import DEFAULT_CLASS, DEFAULT_SUBJECT


def _greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning 👋"
    if hour < 17:
        return "Good afternoon 👋"
    return "Good evening 👋"


def render_home():
    render_hero(
        _greeting(),
        "Welcome back to EduRAG — your AI-powered NCERT companion.",
        ["Learn smarter. Practice better. Understand deeper."],
    )

    # --- Ask EduRAG quick input -------------------------------------------
    st.markdown("### Ask EduRAG")
    with st.form("home_ask_form", clear_on_submit=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            query = st.text_input(
                "Ask", placeholder="🔍 Ask anything about your NCERT textbooks...",
                label_visibility="collapsed",
            )
        with c2:
            submitted = st.form_submit_button("➤ Ask", use_container_width=True, type="primary")
    st.caption("🎤 Voice and 📎 image input are available on the AI Tutor screen.")

    if submitted and query.strip():
        st.session_state.pending_prompt = query.strip()
        st.session_state.view = "tutor"
        st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # --- Quick actions -------------------------------------------------
    st.markdown("### Quick Actions")
    cols = st.columns(4)
    actions = [
        ("🤖", "Ask EduRAG", "Ask questions directly from NCERT.", "tutor"),
        ("🧠", "Practice", "Generate questions based on selected topics.", "practice"),
        ("📝", "Take a Quiz", "Test your knowledge.", "quiz"),
        ("📊", "View Progress", "See learning performance.", "progress"),
    ]
    for col, (icon, title, desc, target) in zip(cols, actions):
        with col:
            if quick_action(icon, title, desc, "Open →", key=f"qa_{target}"):
                st.session_state.view = target
                st.rerun()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # --- Continue Learning (real chapters, real accuracy where available) -
    st.markdown("### Continue Learning")
    chapters = get_library_chapters()
    stats = progress_store.get_stats()
    chapter_progress = stats["chapter_accuracy"]

    if chapters:
        cols = st.columns(4)
        for i, ch in enumerate(chapters[:4]):
            with cols[i % 4]:
                with st.container(border=True):
                    st.markdown("<div class='subject-card-icon'>📘</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='subject-card-title'>{ch['title']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='subject-card-meta'>{DEFAULT_SUBJECT}, {DEFAULT_CLASS}</div>",
                                unsafe_allow_html=True)
                    pct = chapter_progress.get(ch["title"])
                    if pct is not None:
                        render_progress_bar(pct)
                        st.caption(f"{pct}% accuracy so far")
                    else:
                        st.caption("Not practiced yet")
                    if st.button("Continue →", key=f"cont_{ch['file']}", use_container_width=True):
                        st.session_state.selected_chapter = ch["title"]
                        st.session_state.view = "tutor"
                        st.rerun()
    else:
        st.info("No chapters indexed yet — add PDFs to data/ and run ingest.py.")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # --- Recent Activity (real, from progress_store) -----------------------
    st.markdown("### Recent Activity")
    recent = stats["recent_activity"]
    if not recent:
        st.caption("Nothing yet — ask a question, or try a Practice/Quiz session to see activity here.")
    else:
        icons = {"tutor": "⚡", "practice": "🧠", "quiz": "📝"}
        for item in recent[:6]:
            ts = datetime.fromisoformat(item["timestamp"])
            when = ts.strftime("%b %d, %I:%M %p")
            st.markdown(
                f"""<div class="glass-card fadein" style="padding:0.75rem 1rem; margin-bottom:0.5rem;">
                {icons.get(item['type'], '•')} <strong>{item['detail']}</strong><br/>
                <span class="text-secondary">{item['subject']} • {item['chapter']} • {when}</span>
                </div>""",
                unsafe_allow_html=True,
            )
