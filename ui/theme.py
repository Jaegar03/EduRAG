# ui/theme.py
"""
Central design system for EduRAG: color tokens + the one CSS injection
that restyles Streamlit's default chrome into a dark AI-education product
look. Keep every color here — components reference these tokens instead of
hardcoding hex values so the theme stays consistent and easy to retune.
"""
import streamlit as st

BG = "#080B14"
BG_SECONDARY = "#0F1422"
CARD = "#151B2B"
ACCENT = "#7C5CFF"
ACCENT_2 = "#20C7FF"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#F87171"
TEXT = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"
BORDER = "rgba(255,255,255,0.08)"
GRADIENT = f"linear-gradient(135deg, {ACCENT} 0%, {ACCENT_2} 100%)"

CSS = f"""
<style>

/* ============ 1. STREAMLIT CHROME OVERRIDES ============ */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{
    background: transparent;
}}
div.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}}
[data-testid="stDecoration"] {{ display: none; }}

/* ============ 2. BASE / TYPOGRAPHY ============ */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: {BG};
    color: {TEXT};
}}
[data-testid="stAppViewContainer"] * {{
    font-family: "Segoe UI", "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}}
/* Streamlit's built-in icons (sidebar collapse arrow, expander chevron, etc.)
   are text ligatures ("keyboard_double_arrow_left") rendered through a
   dedicated icon font. The universal font-family rule above clobbers that,
   so the ligature text shows up literally instead of turning into a glyph.
   Restore it specifically for those elements. */
[data-testid="stIconMaterial"] {{
    font-family: "Material Symbols Rounded" !important;
}}
h1, h2, h3, h4 {{
    color: {TEXT};
    font-weight: 700;
    letter-spacing: -0.01em;
}}
p, span, label, .stMarkdown {{
    color: {TEXT};
}}
.text-secondary {{ color: {TEXT_SECONDARY} !important; }}
a {{ color: {ACCENT_2}; }}
hr {{ border-color: {BORDER}; }}

::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {CARD}; border-radius: 8px; }}

/* ============ 3. SIDEBAR ============ */
[data-testid="stSidebar"] {{
    background-color: {BG_SECONDARY};
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.25rem;
}}
.sidebar-brand {{
    font-size: 1.35rem;
    font-weight: 800;
    color: {TEXT};
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0 0.25rem;
}}
.sidebar-tagline {{
    color: {TEXT_SECONDARY};
    font-size: 0.8rem;
    padding: 0.15rem 0.25rem 1rem 0.25rem;
}}
[data-testid="stSidebar"] [data-testid="stButton"] > button {{
    background: transparent;
    border: 1px solid transparent;
    color: {TEXT_SECONDARY};
    text-align: left;
    justify-content: flex-start;
    font-weight: 500;
    padding: 0.55rem 0.9rem;
    border-radius: 10px;
    transition: all 0.15s ease;
}}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {{
    background: rgba(124, 92, 255, 0.10);
    color: {TEXT};
    border-color: {BORDER};
}}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {{
    background: {GRADIENT};
    color: {TEXT};
    border: none;
    box-shadow: 0 4px 14px rgba(124, 92, 255, 0.35);
}}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"]:hover {{
    filter: brightness(1.06);
}}

/* ============ 4. BUTTONS (main content) ============ */
[data-testid="stButton"] > button {{
    border-radius: 10px;
    border: 1px solid {BORDER};
    background: {CARD};
    color: {TEXT};
    font-weight: 600;
    padding: 0.5rem 1rem;
    transition: all 0.15s ease;
}}
[data-testid="stButton"] > button:hover {{
    border-color: {ACCENT};
    color: {TEXT};
    box-shadow: 0 0 0 1px {ACCENT} inset;
}}
[data-testid="stButton"] > button[kind="primary"] {{
    background: {GRADIENT};
    border: none;
    box-shadow: 0 4px 14px rgba(124, 92, 255, 0.30);
}}
[data-testid="stButton"] > button[kind="primary"]:hover {{
    filter: brightness(1.07);
}}
[data-testid="stButton"] > button:focus:not(:active) {{
    color: {TEXT};
}}

/* ============ 5. INPUTS / CHAT INPUT / UPLOADER / SELECT ============ */
[data-testid="stChatInput"] {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
}}
[data-testid="stChatInput"] textarea {{
    color: {TEXT};
}}
.stTextInput input, .stTextArea textarea, .stNumberInput input {{
    background: {CARD} !important;
    color: {TEXT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 1px {ACCENT} !important;
}}
div[data-baseweb="select"] > div {{
    background: {CARD} !important;
    border-color: {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
}}
[data-testid="stFileUploaderDropzone"] {{
    background: {BG_SECONDARY};
    border: 1.5px dashed {BORDER};
    border-radius: 14px;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: {ACCENT};
}}
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label {{
    color: {TEXT};
}}

/* ============ 6. CONTAINERS-AS-CARDS ============ */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {{
    /* default bordered container theming; specific cards below refine further */
}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 16px !important;
}}

/* Generic card surfaces used via st.markdown */
.glass-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}}
.metric-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 1rem 1.1rem;
    text-align: left;
}}
.metric-card .metric-value {{
    font-size: 1.6rem;
    font-weight: 800;
    color: {TEXT};
}}
.metric-card .metric-label {{
    color: {TEXT_SECONDARY};
    font-size: 0.82rem;
    margin-top: 0.15rem;
}}
.subject-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 1.1rem 1.2rem 0.6rem 1.2rem;
    transition: border-color 0.15s ease, transform 0.15s ease;
}}
.subject-card:hover {{
    border-color: {ACCENT};
    transform: translateY(-2px);
}}
.subject-card-icon {{ font-size: 1.6rem; margin-bottom: 0.35rem; }}
.subject-card-title {{ font-weight: 700; color: {TEXT}; font-size: 1.02rem; }}
.subject-card-meta {{ color: {TEXT_SECONDARY}; font-size: 0.8rem; margin: 0.2rem 0 0.6rem 0; }}

.progress-track {{
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 8px;
    width: 100%;
    overflow: hidden;
    margin: 0.35rem 0;
}}
.progress-fill {{
    height: 100%;
    border-radius: 999px;
    background: {GRADIENT};
}}

/* ============ 7. HERO ============ */
.hero {{
    background: radial-gradient(circle at top left, rgba(124,92,255,0.20), transparent 60%),
                radial-gradient(circle at bottom right, rgba(32,199,255,0.14), transparent 55%),
                {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 2rem 2.25rem;
    margin-bottom: 1.5rem;
}}
.hero h1 {{
    font-size: 2rem;
    margin: 0 0 0.35rem 0;
}}
.hero p {{
    color: {TEXT_SECONDARY};
    font-size: 1.02rem;
    margin: 0;
}}
.badge-gradient {{
    display: inline-block;
    background: {GRADIENT};
    color: {TEXT};
    font-weight: 700;
    font-size: 0.75rem;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    margin-bottom: 0.75rem;
}}

/* ============ 8. CHAT MESSAGES / SOURCES ============ */
.chat-bubble {{
    border-radius: 16px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    border: 1px solid {BORDER};
}}
.chat-bubble.user {{
    background: {CARD};
}}
.chat-bubble.assistant {{
    background: linear-gradient(180deg, rgba(124,92,255,0.08), rgba(21,27,43,0.4)), {CARD};
}}
.chat-role {{
    font-weight: 700;
    font-size: 0.85rem;
    color: {TEXT_SECONDARY};
    margin-bottom: 0.35rem;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}}
.source-card {{
    background: {BG_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 0.6rem 0.85rem;
    margin-bottom: 0.5rem;
}}
.source-card .source-title {{ font-weight: 700; color: {TEXT}; font-size: 0.88rem; }}
.source-card .source-meta {{ color: {TEXT_SECONDARY}; font-size: 0.78rem; }}

/* ============ 9. TABS / EXPANDERS / METRICS ============ */
[data-testid="stExpander"] {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
[data-testid="stTabs"] button[role="tab"] {{
    color: {TEXT_SECONDARY};
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {TEXT};
    border-bottom-color: {ACCENT};
}}
[data-testid="stMetric"] {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 0.85rem 1rem;
}}
[data-testid="stMetricLabel"] {{ color: {TEXT_SECONDARY}; }}
[data-testid="stMetricValue"] {{ color: {TEXT}; }}

/* ============ 10. MISC / EMPTY & ERROR STATES / ANIMATIONS ============ */
.empty-state {{
    text-align: center;
    padding: 3rem 1.5rem;
    color: {TEXT_SECONDARY};
    border: 1px dashed {BORDER};
    border-radius: 16px;
    background: {BG_SECONDARY};
}}
.empty-state .empty-icon {{ font-size: 2.4rem; margin-bottom: 0.6rem; }}
.empty-state .empty-title {{ color: {TEXT}; font-weight: 700; font-size: 1.05rem; margin-bottom: 0.3rem; }}

.error-card {{
    background: rgba(248, 113, 113, 0.08);
    border: 1px solid rgba(248, 113, 113, 0.35);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    color: {TEXT};
}}
.error-card .error-title {{ font-weight: 700; color: {DANGER}; margin-bottom: 0.25rem; }}

.chip {{
    display: inline-block;
    background: rgba(124,92,255,0.12);
    color: {ACCENT_2};
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    border: 1px solid rgba(124,92,255,0.25);
}}

@keyframes fadein {{
    from {{ opacity: 0; transform: translateY(4px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.fadein {{ animation: fadein 0.25s ease; }}

</style>
"""


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)
