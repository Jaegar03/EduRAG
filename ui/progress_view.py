# ui/progress_view.py
from datetime import date, timedelta

import plotly.graph_objects as go
import streamlit as st

import progress_store
from ui.components import render_empty_state, render_metric_card, section_header
from ui.theme import ACCENT, BORDER, CARD, TEXT, TEXT_SECONDARY, WARNING


def _subject_bar_chart(subject_accuracy: dict):
    subjects = list(subject_accuracy.keys())
    values = list(subject_accuracy.values())
    colors = [ACCENT if v >= 70 else (WARNING if v >= 50 else "#F87171") for v in values]

    fig = go.Figure(go.Bar(
        x=values, y=subjects, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v}%" for v in values], textposition="outside",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT), margin=dict(l=10, r=30, t=10, b=10),
        xaxis=dict(range=[0, 100], gridcolor=BORDER, color=TEXT_SECONDARY, ticksuffix="%"),
        yaxis=dict(color=TEXT), height=90 + 45 * len(subjects),
    )
    return fig


def _activity_heatmap(activity_dates: list):
    today = date.today()
    weeks = 12
    start = today - timedelta(days=weeks * 7 - 1)
    date_set = set(activity_dates)

    z, hover = [], []
    for wd in range(7):  # Mon..Sun rows
        row, row_hover = [], []
        for w in range(weeks):
            d = start + timedelta(days=w * 7 + wd)
            active = 1 if d in date_set else 0
            row.append(active if d <= today else None)
            row_hover.append(d.strftime("%b %d"))
        z.append(row)
        hover.append(row_hover)

    fig = go.Figure(go.Heatmap(
        z=z, text=hover, hoverinfo="text",
        colorscale=[[0, CARD], [1, ACCENT]],
        showscale=False, xgap=3, ygap=3,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10), height=160,
        xaxis=dict(visible=False), yaxis=dict(
            tickvals=list(range(7)),
            ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            color=TEXT_SECONDARY, autorange="reversed",
        ),
    )
    return fig


def render_progress():
    section_header("📊 Learning Progress", "Track your growth and identify what to improve.")

    stats = progress_store.get_stats()

    if stats["total_sessions"] == 0:
        render_empty_state(
            "📊", "No progress data yet",
            "Complete a Practice set or Quiz to start building your learning analytics.",
        )
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("🔥", f"{stats['streak']} Day", "Streak")
    with c2:
        render_metric_card("❓", stats["total_questions"], "Questions Attempted")
    with c3:
        render_metric_card("🧩", stats["concepts"], "Chapters Covered")
    with c4:
        render_metric_card("🎯", f"{stats['accuracy']}%", "Accuracy")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    st.markdown("### Subject Performance")
    if stats["subject_accuracy"]:
        st.plotly_chart(_subject_bar_chart(stats["subject_accuracy"]), use_container_width=True)
    else:
        st.caption("No subject-level data yet.")

    st.markdown("### Topics to Review")
    weak = [t for t in stats["weak_topics"] if t[1] < 70]
    if weak:
        for chapter, acc in weak:
            st.markdown(f"⚠ **{chapter}** — {acc}%")
        if st.button("Practice these topics →"):
            st.session_state.view = "practice"
            st.rerun()
    else:
        st.caption("No weak topics detected yet — keep practicing!")

    st.markdown("### Learning Activity")
    st.plotly_chart(_activity_heatmap(stats["activity_dates"]), use_container_width=True)
