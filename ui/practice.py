# ui/practice.py
import streamlit as st

import progress_store
from ui.components import render_empty_state, render_error_state, render_progress_bar, section_header
from ui.library import get_library_chapters
from ui.rag import generate_questions_for
from ui.state import DEFAULT_CLASS, DEFAULT_SUBJECT


def _new_state(subject, chapter_file, chapter_title, difficulty, num_questions, questions):
    return {
        "subject": subject, "chapter_file": chapter_file, "chapter_title": chapter_title,
        "difficulty": difficulty, "num_questions": num_questions,
        "questions": questions, "index": 0, "answers": {}, "submitted_current": False,
        "finished": False, "logged": False,
    }


def render_practice():
    section_header("🧠 Practice Arena", "Strengthen your understanding with AI-generated questions.")

    chapters = get_library_chapters()
    if not chapters:
        render_empty_state("🧠", "No content indexed yet",
                            "Add NCERT PDFs to data/ and run ingest.py before generating practice questions.")
        return
    chapter_titles = [c["title"] for c in chapters]
    title_to_file = {c["title"]: c["file"] for c in chapters}

    state = st.session_state.practice_state

    if state is None or st.session_state.get("_practice_reconfig"):
        st.session_state._practice_reconfig = False
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                st.selectbox("Subject", [DEFAULT_SUBJECT], disabled=True, key="pr_subject")
            with c2:
                st.selectbox("Class", [DEFAULT_CLASS], disabled=True, key="pr_class")
            chapter_title = st.selectbox("Chapter", chapter_titles, key="pr_chapter")
            difficulty = st.radio("Difficulty", ["Easy", "Medium", "Hard"], horizontal=True, key="pr_difficulty")
            num_questions = st.selectbox("Questions", [3, 5, 8, 10], index=1, key="pr_num")

            if st.button("Generate Practice Set", type="primary", use_container_width=True):
                with st.spinner("EduRAG is writing your questions from the textbook..."):
                    try:
                        questions = generate_questions_for(
                            title_to_file[chapter_title], chapter_title, difficulty, num_questions,
                        )
                        st.session_state.practice_state = _new_state(
                            DEFAULT_SUBJECT, title_to_file[chapter_title], chapter_title,
                            difficulty, num_questions, questions,
                        )
                        st.rerun()
                    except Exception as e:
                        render_error_state(
                            "Couldn't generate questions",
                            "EduRAG couldn't turn this chapter into practice questions right now.",
                            str(e),
                        )
        return

    if state["finished"]:
        _render_summary(state)
        return

    _render_question(state)


def _render_question(state):
    total = len(state["questions"])
    idx = state["index"]
    q = state["questions"][idx]

    st.caption(f"{state['chapter_title']} • {state['difficulty']}")
    st.markdown(f"**QUESTION {idx + 1:02d} / {total:02d}**")
    render_progress_bar((idx / total) * 100)

    with st.container(border=True):
        st.markdown(q["question"])
        answered = idx in state["answers"]
        choice = st.radio(
            "Options", q["options"], key=f"practice_choice_{idx}",
            index=state["answers"].get(idx, {}).get("selected") if answered else None,
            label_visibility="collapsed",
        )

        if not state["submitted_current"]:
            if st.button("Submit Answer →", type="primary", use_container_width=True, key=f"submit_{idx}"):
                selected_index = q["options"].index(choice)
                is_correct = selected_index == q["correct_index"]
                state["answers"][idx] = {"selected": selected_index, "correct": is_correct}
                state["submitted_current"] = True
                st.rerun()
        else:
            result = state["answers"][idx]
            if result["correct"]:
                st.success("✓ Correct!")
            else:
                correct_text = q["options"][q["correct_index"]]
                st.error(f"✗ Not quite. Correct answer: {correct_text}")
            if q.get("explanation"):
                st.info(q["explanation"])

            nav_label = "Next Question →" if idx + 1 < total else "Finish Practice 🎉"
            if st.button(nav_label, type="primary", use_container_width=True, key=f"next_{idx}"):
                if idx + 1 < total:
                    state["index"] += 1
                    state["submitted_current"] = False
                else:
                    state["finished"] = True
                st.rerun()

    if st.button("Cancel practice set", key="cancel_practice"):
        st.session_state.practice_state = None
        st.rerun()


def _render_summary(state):
    total = len(state["questions"])
    correct = sum(1 for a in state["answers"].values() if a["correct"])
    accuracy = round((correct / total) * 100) if total else 0

    if not state["logged"]:
        progress_store.log_practice_result(state["subject"], state["chapter_title"], state["difficulty"], total, correct)
        state["logged"] = True

    st.markdown(
        f"""
        <div class="glass-card fadein" style="text-align:center;">
            <h2>Practice Complete 🎉</h2>
            <p style="font-size:1.4rem; font-weight:800;">{correct} / {total} Correct</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Accuracy", f"{accuracy}%")
    with c2:
        st.metric("Concepts", state["chapter_title"])
    with c3:
        needs_review = total - correct
        st.metric("Needs Review", needs_review)

    with st.expander("Review Answers"):
        for i, q in enumerate(state["questions"]):
            result = state["answers"].get(i, {})
            mark = "✅" if result.get("correct") else "❌"
            st.markdown(f"{mark} **Q{i+1}.** {q['question']}")
            st.caption(f"Correct answer: {q['options'][q['correct_index']]}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Practice Again", use_container_width=True, type="primary"):
            st.session_state.practice_state = None
            st.session_state._practice_reconfig = True
            st.rerun()
    with c2:
        if st.button("Back to Home", use_container_width=True):
            st.session_state.practice_state = None
            st.session_state.view = "home"
            st.rerun()
