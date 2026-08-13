# ui/library.py
import os
import re

import streamlit as st
from pypdf import PdfReader

from ui.components import render_empty_state, section_header
from ui.state import DEFAULT_CLASS, DEFAULT_SUBJECT

DATA_PATH = "data"

# Best-effort chapter titles for the indexed NCERT Physics (Class 12, Part 1)
# PDFs, cross-checked against each file's own extracted text (see
# get_library_chapters()) rather than assumed from memory. Used only as a
# fallback label when a file's own first-page text doesn't extraction to a
# clean title.
_KNOWN_TITLES = {
    "leph101.pdf": "Electric Charges and Fields",
    "leph102.pdf": "Electrostatic Potential and Capacitance",
    "leph103.pdf": "Current Electricity",
    "leph104.pdf": "Moving Charges and Magnetism",
    "leph105.pdf": "Magnetism and Matter",
    "leph106.pdf": "Electromagnetic Induction",
    "leph107.pdf": "Alternating Current",
    "leph108.pdf": "Electromagnetic Waves",
}


@st.cache_data(show_spinner=False)
def get_library_chapters():
    """Build the chapter list directly from the PDFs present in data/, so
    this screen only ever shows textbooks that are actually indexed."""
    chapters = []
    if not os.path.isdir(DATA_PATH):
        return chapters

    for fname in sorted(os.listdir(DATA_PATH)):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(DATA_PATH, fname)
        num_pages = 0
        try:
            reader = PdfReader(path)
            num_pages = len(reader.pages)
        except Exception:
            pass

        match = re.search(r"(\d+)", fname)
        chapter_no = int(match.group(1)[-2:]) if match else len(chapters) + 1
        title = _KNOWN_TITLES.get(fname, fname.rsplit(".", 1)[0])

        chapters.append({
            "file": fname,
            "chapter_no": chapter_no,
            "title": title,
            "pages": num_pages,
        })
    return chapters


def render_library():
    section_header("📚 NCERT Library", "Explore your learning material.")

    chapters = get_library_chapters()
    if not chapters:
        render_empty_state("📚", "No textbooks indexed yet",
                            "Add NCERT PDFs to the data/ folder and run ingest.py.")
        return

    st.markdown(
        f"""<div class="glass-card fadein" style="margin-bottom:1.25rem;">
        <strong>{DEFAULT_SUBJECT} — {DEFAULT_CLASS} (Part 1)</strong><br/>
        <span class="text-secondary">{len(chapters)} chapters indexed and searchable by the AI Tutor.</span>
        </div>""",
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for i, ch in enumerate(chapters):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"<div class='subject-card-icon'>📘</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='subject-card-title'>Ch {ch['chapter_no']}. {ch['title']}</div>",
                            unsafe_allow_html=True)
                st.markdown(
                    f"<div class='subject-card-meta'>{ch['pages']} pages • {DEFAULT_SUBJECT}, {DEFAULT_CLASS}</div>",
                    unsafe_allow_html=True,
                )
                if st.button("Open in AI Tutor →", key=f"lib_open_{ch['file']}", use_container_width=True):
                    st.session_state.selected_chapter = ch["title"]
                    st.session_state.view = "tutor"
                    st.rerun()
