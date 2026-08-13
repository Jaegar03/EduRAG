# ui/profile.py
import streamlit as st

import progress_store
from ui.components import section_header


def render_profile():
    section_header("👤 Profile", "")

    stats = progress_store.get_stats()

    with st.container(border=True):
        st.markdown(f"### {_display_name()}")
        st.caption("Student")
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Learning Streak", f"{stats['streak']} days")
            st.metric("Average Accuracy", f"{stats['accuracy']}%")
        with c2:
            st.metric("Questions Attempted", stats["total_questions"])
            st.metric("Chapters Covered", stats["concepts"])

        st.markdown("---")
        st.markdown("**Achievements**")
        achievements = []
        if stats["streak"] >= 1:
            achievements.append("🔥 Consistent Learner")
        if stats["concepts"] >= 3:
            achievements.append("🧠 Concept Explorer")
        if stats["total_sessions"] >= 5:
            achievements.append("🏆 Quiz Performer")
        if stats["total_questions"] >= 1:
            achievements.append("📚 NCERT Explorer")

        if achievements:
            for a in achievements:
                st.markdown(a)
        else:
            st.caption("Complete a practice set or quiz to start earning achievements.")


def _display_name():
    # No auth/user-accounts system exists yet, so this is a generic
    # placeholder — structured so a real logged-in user's name can replace
    # it in one place once accounts are added.
    return "EduRAG Student"
