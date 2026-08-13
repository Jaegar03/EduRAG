# ui/tutor.py
import streamlit as st

import progress_store
from ui.components import render_chat_message, render_empty_state, render_error_state, section_header
from ui.library import get_library_chapters
from ui.rag import ask_question, detect_language, process_image_input, text_to_speech
from ui.state import DEFAULT_CLASS, DEFAULT_SUBJECT


def process_voice_input():
    """
    Records via sounddevice (no PyAudio/compiler needed) and transcribes
    with Google's speech recognition. Returns the transcribed text or None.

    Note: this records on whatever machine is running the Streamlit
    process. That's the visitor's own machine when run locally, but on a
    cloud deployment it's the server's (non-existent) microphone — so on
    a hosted deploy this will reliably fail at the "no input device" step
    and show a graceful warning rather than transcribe anything. Import
    itself is guarded broadly below since a missing native PortAudio
    library raises OSError, not ImportError, and must not crash the page.
    """
    try:
        import speech_recognition as sr
        import sounddevice as sd
    except (ImportError, OSError):
        st.warning("🎤 Voice input isn't available in this environment.")
        return None

    RECORD_SECONDS = 5
    SAMPLE_RATE = 16000

    st.caption(f"🎤 Click and speak your question (records for {RECORD_SECONDS}s)")
    if st.button("🎙️ Start Recording", key="voice_button", use_container_width=True):
        try:
            with st.spinner("Listening... Speak now!"):
                recording = sd.rec(
                    int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                    channels=1, dtype="int16",
                )
                sd.wait()

            with st.spinner("Processing speech..."):
                audio_data = sr.AudioData(recording.tobytes(), SAMPLE_RATE, 2)
                r = sr.Recognizer()
                text = r.recognize_google(audio_data)
                st.success(f"🎯 I heard: '{text}'")
                return text

        except sr.UnknownValueError:
            st.warning("🤔 Sorry, I couldn't understand what you said. Please try again.")
        except sr.RequestError as e:
            st.error(f"❌ Speech recognition error: {e}")
        except sd.PortAudioError as e:
            st.warning(f"🎤 No microphone detected on this server: {e}")
        except Exception as e:
            st.warning(f"🎤 Voice input failed: {e}")
    return None


def _handle_turn(prompt, image_data):
    """Runs one full ask→answer turn and appends it to chat history."""
    user_message = {"role": "user", "content": prompt or "Please analyze this image"}
    if image_data:
        user_message["image"] = image_data["image"]
        user_message["has_image"] = True
    st.session_state.messages.append(user_message)

    with st.spinner("Thinking..."):
        try:
            result = ask_question(prompt, image_data)
            response_text = result["response"]
            sources = result["sources"]

            st.session_state.messages.append({
                "role": "assistant", "content": response_text, "sources": sources,
            })

            chapter = sources[0]["source"] if sources else (st.session_state.selected_chapter or "General")
            progress_store.log_activity("tutor", DEFAULT_SUBJECT, chapter, (prompt or "Image question")[:80])

            try:
                st.session_state["_last_audio"] = text_to_speech(response_text)
            except Exception:
                st.session_state["_last_audio"] = None

        except Exception as e:
            from ui.rag import friendly_error_message
            error_msg = friendly_error_message(e)
            st.session_state.messages.append({
                "role": "assistant", "content": error_msg, "error_detail": str(e),
            })


def render_ai_tutor():
    section_header("🤖 AI Tutor", "Your personal NCERT study companion")

    chapters = get_library_chapters()
    chapter_titles = [c["title"] for c in chapters]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.selectbox("Class", [DEFAULT_CLASS], disabled=True)
    with col2:
        st.selectbox("Subject", [DEFAULT_SUBJECT], disabled=True)
    with col3:
        if chapter_titles:
            default_idx = chapter_titles.index(st.session_state.selected_chapter) \
                if st.session_state.selected_chapter in chapter_titles else 0
            st.session_state.selected_chapter = st.selectbox(
                "Chapter (context hint)", chapter_titles, index=default_idx,
            )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # A prompt queued from the Home screen's quick-ask input.
    if st.session_state.pending_prompt:
        pending = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        _handle_turn(pending, None)

    if not st.session_state.messages:
        render_empty_state(
            "🤖", "Ask EduRAG something",
            "Your NCERT knowledge companion is ready. Ask about any concept in the indexed chapters.",
        )
    else:
        for message in st.session_state.messages:
            if message["role"] == "assistant" and message.get("error_detail"):
                render_error_state("Something went wrong", message["content"], message["error_detail"])
            else:
                render_chat_message(
                    message["role"], message["content"],
                    image=message.get("image"), sources=message.get("sources"),
                )

    last_audio = st.session_state.get("_last_audio")
    if last_audio is not None:
        st.markdown("**🔊 Listen to the last response:**")
        st.audio(last_audio, format="audio/mp3")

    st.markdown("### 💬 Ask your question")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        text_input = st.chat_input("Type your question here...")
    with col2:
        st.markdown("**🎤 Voice**")
        voice_text = process_voice_input()
    with col3:
        st.markdown("**🖼️ Image**")
        uploaded_image = st.file_uploader(
            "Upload an image", type=["png", "jpg", "jpeg"],
            key="image_uploader", label_visibility="collapsed",
        )

    prompt = text_input or voice_text
    image_data = process_image_input(uploaded_image) if uploaded_image else None

    if prompt or image_data:
        _handle_turn(prompt, image_data)
        st.rerun()
