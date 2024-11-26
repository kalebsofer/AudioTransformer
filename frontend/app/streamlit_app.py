# frontend streamlit app goes here
import streamlit as st
import requests
import uuid
# from config.settings import get_settings
from logs import log_manager

# settings = get_settings()

st.set_page_config(page_title="Transcription Service", layout="wide")

st.title("Transcriptiopn Service")

# Initialize session states
if "audio_uploaded" not in st.session_state:
    st.session_state.audio_uploaded = False
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "audio_id" not in st.session_state:
    st.session_state.audio_id = None
if "uploaded_audio" not in st.session_state:
    st.session_state.uploaded_audio = None

# Reset function to handle new uploads
def reset_state():
    st.session_state.audio_uploaded = False
    st.session_state.transcript = None
    st.session_state.feedback_submitted = False
    st.session_state.audio_id = None
    st.session_state.uploaded_audio = None

# Upload audio
uploaded_audio = st.file_uploader("Upload an soundbite", type=["mp3", "wav", "m4a"])

if uploaded_audio is not None and not st.session_state.audio_uploaded:
    # Store the uploaded audio in session state
    st.session_state.uploaded_audio = uploaded_audio
    st.session_state.audio_uploaded = True
    st.session_state.audio_id = str(uuid.uuid4())

# Display the uploaded audio if available
if st.session_state.audio_uploaded:
    st.audio(st.session_state.uploaded_audio, transcript="Uploaded audio", format = "audio/mp3")

    # Submit button to generate transcript
    if st.button("Generate transcript") and st.session_state.transcript is None:
        try:
            files = {"file": st.session_state.uploaded_audio.getvalue()}
            data = {"audio_id": st.session_state.audio_id}
            response = requests.post(
                f"{settings.BACKEND_URL}/generate-transcript",
                files=files,
                data=data,
                timeout=settings.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            result = response.json()
            st.session_state.transcript = result.get("transcript", "No transcript generated.")

            # Log the generated transcript
            log_manager.log_transcript(
                audio_id=st.session_state.audio_id,
                generated_transcript=st.session_state.transcript,
                feedback_received=False,
                rating=None,
                ideal_transcript=None,
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend service: {str(e)}")

# Display the generated transcript and feedback form
if st.session_state.transcript and not st.session_state.feedback_submitted:
    st.subheader("Generated transcript:")
    st.write(st.session_state.transcript)

    st.subheader("Provide Feedback")
    score = st.slider("Rate the transcript (1-10)", 1, 10, 5)
    user_transcript = st.text_input("Please provide an accurate transcript")

    # Submit feedback button
    if st.button("Submit Feedback"):
        log_manager.log_transcript(
            audio_id=st.session_state.audio_id,
            generated_transcript=st.session_state.transcript,
            feedback_received=True,
            rating=score,
            ideal_transcript=user_transcript,
        )
        st.success("Thank you for your feedback!")
        st.session_state.feedback_submitted = True

# Option to upload another audio after feedback is submitted
if st.session_state.feedback_submitted:
    if st.button("Upload Another audio file"):
        reset_state()