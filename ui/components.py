# ui/components.py
"""
Reusable, presentation-only building blocks shared across screens.
"""
import html

import streamlit as st


def section_header(title: str, subtitle: str = ""):
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<p class='text-secondary' style='margin-top:-0.6rem;'>{html.escape(subtitle)}</p>",
                     unsafe_allow_html=True)


def render_hero(greeting: str, title: str, lines: list[str]):
    body = "<br/>".join(html.escape(l) for l in lines)
    st.markdown(
        f"""
        <div class="hero fadein">
            <span class="badge-gradient">🎓 EduRAG</span>
            <h1>{html.escape(greeting)}</h1>
            <p>{html.escape(title)}</p>
            <p style="margin-top:0.75rem;">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(icon: str, value, label: str):
    st.markdown(
        f"""
        <div class="metric-card fadein">
            <div class="metric-value">{icon} {html.escape(str(value))}</div>
            <div class="metric-label">{html.escape(label)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress_bar(pct: float):
    pct = max(0, min(100, pct))
    st.markdown(
        f"""<div class="progress-track"><div class="progress-fill" style="width:{pct}%;"></div></div>""",
        unsafe_allow_html=True,
    )


def quick_action(icon: str, title: str, description: str, button_label: str, key: str) -> bool:
    """Renders a bordered card with a title/description and a full-width
    button inside it; returns True the render this card's button was clicked."""
    with st.container(border=True):
        st.markdown(f"<div class='subject-card-icon'>{icon}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='subject-card-title'>{html.escape(title)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='subject-card-meta'>{html.escape(description)}</div>", unsafe_allow_html=True)
        return st.button(button_label, key=key, use_container_width=True, type="secondary")


def render_source_card(source: str, page):
    st.markdown(
        f"""
        <div class="source-card">
            <div class="source-title">📘 {html.escape(str(source))}</div>
            <div class="source-meta">Page {html.escape(str(page))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources: list[dict]):
    if not sources:
        return
    with st.expander(f"📚 Sources ({len(sources)})"):
        for s in sources:
            render_source_card(s.get("source", "Unknown"), s.get("page", "N/A"))


def render_chat_message(role: str, content: str, image=None, sources=None):
    css_class = "user" if role == "user" else "assistant"
    icon = "👤" if role == "user" else "🤖"
    label = "You" if role == "user" else "EduRAG"
    st.markdown(f"<div class='chat-bubble {css_class} fadein'>", unsafe_allow_html=True)
    st.markdown(f"<div class='chat-role'>{icon} {label}</div>", unsafe_allow_html=True)
    st.markdown(content)
    if image is not None:
        st.image(image, caption="Uploaded image", width=280)
    st.markdown("</div>", unsafe_allow_html=True)
    if sources:
        render_sources(sources)


def render_empty_state(icon: str, title: str, description: str, cta_label: str = "", cta_key: str = ""):
    st.markdown(
        f"""
        <div class="empty-state fadein">
            <div class="empty-icon">{icon}</div>
            <div class="empty-title">{html.escape(title)}</div>
            <div>{html.escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if cta_label:
        _, mid, _ = st.columns([1, 1, 1])
        with mid:
            return st.button(cta_label, key=cta_key or f"cta_{title}", use_container_width=True, type="primary")
    return False


def render_error_state(title: str, description: str, debug_detail: str = ""):
    st.markdown(
        f"""
        <div class="error-card fadein">
            <div class="error-title">⚠️ {html.escape(title)}</div>
            <div>{html.escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if debug_detail and st.session_state.get("show_debug"):
        with st.expander("🔧 Technical details (debug mode)"):
            st.code(debug_detail)
