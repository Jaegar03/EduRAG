# ui/sidebar.py
import streamlit as st

from ui.state import NAV_ITEMS

LANGUAGES = {
    "en": "🇺🇸 English", "hi": "🇮🇳 हिंदी (Hindi)", "bn": "🇧🇩 বাংলা (Bengali)",
    "te": "🇮🇳 తెలుగు (Telugu)", "mr": "🇮🇳 मराठी (Marathi)", "ta": "🇮🇳 தமிழ் (Tamil)",
    "ur": "🇵🇰 اردو (Urdu)", "gu": "🇮🇳 ગુજરાતી (Gujarati)", "kn": "🇮🇳 ಕನ್ನಡ (Kannada)",
    "ml": "🇮🇳 മലയാളം (Malayalam)", "es": "🇪🇸 Español", "fr": "🇫🇷 Français",
    "de": "🇩🇪 Deutsch", "zh": "🇨🇳 中文", "ar": "🇸🇦 العربية",
}


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🎓 <span>EduRAG</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-tagline">AI-powered NCERT learning</div>', unsafe_allow_html=True)

        for key, icon, label in NAV_ITEMS:
            active = st.session_state.view == key
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.view = key
                st.rerun()

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        st.markdown("---")

        if st.button("👤  Profile", key="nav_profile", use_container_width=True,
                      type="primary" if st.session_state.view == "profile" else "secondary"):
            st.session_state.view = "profile"
            st.rerun()

        with st.expander("⚙️ Settings"):
            if st.button("🗑️ Clear conversation", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_context = ""
                st.rerun()

            st.session_state.user_language = st.selectbox(
                "Preferred language",
                options=list(LANGUAGES.keys()),
                format_func=lambda code: LANGUAGES.get(code, code),
                index=list(LANGUAGES.keys()).index(st.session_state.user_language)
                if st.session_state.user_language in LANGUAGES else 0,
            )

            st.session_state.show_debug = st.checkbox("Show debug info", value=st.session_state.show_debug)
            if st.session_state.show_debug:
                st.caption(f"Messages: {len(st.session_state.messages)}")
                st.caption(f"View: {st.session_state.view}")

            st.caption("EduRAG's knowledge is limited to the indexed NCERT textbooks.")
