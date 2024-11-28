import streamlit as st
import requests
import uuid
from config.settings import get_settings
from logs import log_manager

settings = get_settings()

st.set_page_config(page_title="Audio Transcription Service", layout="wide")

st.title("Audio Transcription Service")

if "audio_uploaded" not in st.session_state:
    st.session_state.audio_uploaded = False
if "transcription" not in st.session_state:
    st.session_state.transcription = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "audio_id" not in st.session_state:
    st.session_state.audio_id = None
if "uploaded_audio" not in st.session_state:
    st.session_state.uploaded_audio = None


def reset_state():
    st.session_state.audio_uploaded = False
    st.session_state.transcription = None
    st.session_state.feedback_submitted = False
    st.session_state.audio_id = None
    st.session_state.uploaded_audio = None


uploaded_audio = st.file_uploader("Upload an audio file", type=["mp3", "wav"])

if uploaded_audio is not None and not st.session_state.audio_uploaded:
    st.session_state.uploaded_audio = uploaded_audio
    st.session_state.audio_uploaded = True
    st.session_state.audio_id = str(uuid.uuid4())

if st.session_state.audio_uploaded:
    st.audio(st.session_state.uploaded_audio)

    if st.button("Generate Transcription") and st.session_state.transcription is None:
        try:
            files = {"file": st.session_state.uploaded_audio.getvalue()}
            data = {"audio_id": st.session_state.audio_id}
            response = requests.post(
                f"{settings.BACKEND_URL}/generate-transcription",
                files=files,
                data=data,
                timeout=settings.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            result = response.json()
            st.session_state.transcription = result.get(
                "transcription", "No transcription generated."
            )

            log_manager.log_transcription(
                audio_id=st.session_state.audio_id,
                generated_transcription=st.session_state.transcription,
                feedback_received=False,
                rating=None,
                ideal_transcription=None,
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend service: {str(e)}")

if st.session_state.transcription and not st.session_state.feedback_submitted:
    st.subheader("Generated Transcription:")
    st.write(st.session_state.transcription)

    st.subheader("Provide Feedback")
    score = st.slider("Rate the transcription accuracy (1-10)", 1, 10, 5)
    user_transcription = st.text_area(
        "To improve our moel, please provide the correct transcription."
    )

    if st.button("Submit Feedback"):
        log_manager.log_transcription(
            audio_id=st.session_state.audio_id,
            generated_transcription=st.session_state.transcription,
            feedback_received=True,
            rating=score,
            ideal_transcription=user_transcription,
        )
        st.success("Thank you for your feedback!")
        st.session_state.feedback_submitted = True

if st.session_state.feedback_submitted:
    if st.button("Upload Another Audio"):
        reset_state()
