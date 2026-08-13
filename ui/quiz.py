# ui/quiz.py
import time

import streamlit as st

import progress_store
from ui.components import render_empty_state, render_error_state, render_progress_bar, section_header
from ui.library import get_library_chapters
from ui.rag import generate_questions_for
from ui.state import DEFAULT_CLASS, DEFAULT_SUBJECT


def _new_state(subject, chapter_file, chapter_title, difficulty, num_questions, time_limit_min, questions):
    return {
        "subject": subject, "chapter_file": chapter_file, "chapter_title": chapter_title,
        "difficulty": difficulty, "num_questions": num_questions,
        "time_limit_sec": time_limit_min * 60, "start_time": time.time(),
        "questions": questions, "current": 0, "answers": {},
        "finished": False, "logged": False,
    }


def render_quiz():
    section_header("📝 Quiz Center", "Test your NCERT knowledge under exam conditions.")

    chapters = get_library_chapters()
    if not chapters:
        render_empty_state("📝", "No content indexed yet",
                            "Add NCERT PDFs to data/ and run ingest.py before starting a quiz.")
        return
    chapter_titles = [c["title"] for c in chapters]
    title_to_file = {c["title"]: c["file"] for c in chapters}

    state = st.session_state.quiz_state

    if state is None:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                st.selectbox("Subject", [DEFAULT_SUBJECT], disabled=True)
            with c2:
                st.selectbox("Class", [DEFAULT_CLASS], disabled=True)
            chapter_title = st.selectbox("Chapter", chapter_titles, key="qz_chapter")
            difficulty = st.radio("Difficulty", ["Easy", "Medium", "Hard"], horizontal=True, key="qz_difficulty")
            c3, c4 = st.columns(2)
            with c3:
                num_questions = st.selectbox("Number of questions", [5, 10, 15], index=0, key="qz_num")
            with c4:
                time_limit = st.selectbox("Time limit (minutes)", [5, 10, 15, 20], index=1, key="qz_time")

            if st.button("Start Quiz", type="primary", use_container_width=True):
                with st.spinner("EduRAG is preparing your exam..."):
                    try:
                        questions = generate_questions_for(
                            title_to_file[chapter_title], chapter_title, difficulty, num_questions,
                        )
                        st.session_state.quiz_state = _new_state(
                            DEFAULT_SUBJECT, title_to_file[chapter_title], chapter_title,
                            difficulty, num_questions, time_limit, questions,
                        )
                        st.rerun()
                    except Exception as e:
                        render_error_state(
                            "Couldn't start the quiz",
                            "EduRAG couldn't turn this chapter into quiz questions right now.",
                            str(e),
                        )
        return

    if state["finished"]:
        _render_results(state)
        return

    elapsed = time.time() - state["start_time"]
    remaining = state["time_limit_sec"] - elapsed
    if remaining <= 0:
        state["finished"] = True
        st.rerun()
        return

    _render_quiz_in_progress(state, remaining)


def _render_quiz_in_progress(state, remaining_sec):
    total = len(state["questions"])
    current = state["current"]

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown(f"**Question {current + 1} / {total}**")
        render_progress_bar((len(state["answers"]) / total) * 100)
    with top_r:
        mins, secs = divmod(int(remaining_sec), 60)
        st.markdown(f"<div class='text-secondary'>Time Remaining</div>"
                     f"<div style='font-size:1.4rem; font-weight:800;'>{mins:02d}:{secs:02d}</div>",
                     unsafe_allow_html=True)

    # Question navigator
    nav_cols = st.columns(total)
    for i in range(total):
        status = "✓" if i in state["answers"] else ("●" if i == current else "○")
        with nav_cols[i]:
            if st.button(f"{i+1}\n{status}", key=f"qz_nav_{i}", use_container_width=True):
                state["current"] = i
                st.rerun()

    q = state["questions"][current]
    with st.container(border=True):
        st.markdown(q["question"])
        prior = state["answers"].get(current)
        choice = st.radio(
            "Options", q["options"], key=f"qz_choice_{current}",
            index=prior["selected"] if prior else None, label_visibility="collapsed",
        )
        if choice is not None:
            selected_index = q["options"].index(choice)
            state["answers"][current] = {
                "selected": selected_index,
                "correct": selected_index == q["correct_index"],
            }

    c1, c2, c3 = st.columns(3)
    with c1:
        if current > 0 and st.button("← Previous", use_container_width=True):
            state["current"] -= 1
            st.rerun()
    with c2:
        if current + 1 < total and st.button("Next →", use_container_width=True):
            state["current"] += 1
            st.rerun()
    with c3:
        if st.button("Submit Quiz", type="primary", use_container_width=True):
            state["finished"] = True
            st.rerun()

    st.caption("⏱ Timer updates as you navigate between questions.")


def _render_results(state):
    total = len(state["questions"])
    correct = sum(1 for a in state["answers"].values() if a["correct"])
    pct = round((correct / total) * 100) if total else 0
    time_taken = int(time.time() - state["start_time"])

    if not state["logged"]:
        progress_store.log_quiz_result(
            state["subject"], state["chapter_title"], state["difficulty"], total, correct, time_taken,
        )
        state["logged"] = True

    st.markdown(
        f"""
        <div class="glass-card fadein" style="text-align:center;">
            <h2>🎉 Quiz Completed</h2>
            <p style="font-size:2rem; font-weight:800;">{pct}%</p>
            <p class="text-secondary">{correct} / {total} Correct</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Chapter**")
        st.success(f"✓ {state['chapter_title']}" if pct >= 60 else f"⚠ {state['chapter_title']} (needs review)")
    with c2:
        st.metric("Time taken", f"{time_taken // 60}m {time_taken % 60}s")

    with st.expander("Review Answers"):
        for i, q in enumerate(state["questions"]):
            result = state["answers"].get(i)
            mark = "✅" if result and result["correct"] else ("❌" if result else "⭕ Unanswered")
            st.markdown(f"{mark} **Q{i+1}.** {q['question']}")
            st.caption(f"Correct answer: {q['options'][q['correct_index']]}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Try Again", type="primary", use_container_width=True):
            st.session_state.quiz_state = None
            st.rerun()
    with c2:
        if st.button("Back to Home", use_container_width=True):
            st.session_state.quiz_state = None
            st.session_state.view = "home"
            st.rerun()
