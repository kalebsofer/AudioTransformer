# frontend streamlit app goes here
import streamlit as st
import requests
import uuid
from config.settings import get_settings
from logs import log_manager

settings = get_settings()

st.set_page_config(page_title="Inventive Image Caption", layout="wide")

st.title("Inventive Image Caption")

# Initialize session states
if "image_uploaded" not in st.session_state:
    st.session_state.image_uploaded = False
if "caption" not in st.session_state:
    st.session_state.caption = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "image_id" not in st.session_state:
    st.session_state.image_id = None
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# Reset function to handle new uploads
def reset_state():
    st.session_state.image_uploaded = False
    st.session_state.caption = None
    st.session_state.feedback_submitted = False
    st.session_state.image_id = None
    st.session_state.uploaded_image = None

# Upload image
uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_image is not None and not st.session_state.image_uploaded:
    # Store the uploaded image in session state
    st.session_state.uploaded_image = uploaded_image
    st.session_state.image_uploaded = True
    st.session_state.image_id = str(uuid.uuid4())

# Display the uploaded image if available
if st.session_state.image_uploaded:
    st.image(
        st.session_state.uploaded_image, caption="Uploaded Image", use_column_width=True
    )

    # Submit button to generate caption
    if st.button("Generate Caption") and st.session_state.caption is None:
        try:
            files = {"file": st.session_state.uploaded_image.getvalue()}
            data = {"image_id": st.session_state.image_id}
            response = requests.post(
                f"{settings.BACKEND_URL}/generate-caption",
                files=files,
                data=data,
                timeout=settings.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            result = response.json()
            st.session_state.caption = result.get("caption", "No caption generated.")

            # Log the generated caption
            log_manager.log_caption(
                image_id=st.session_state.image_id,
                generated_caption=st.session_state.caption,
                feedback_received=False,
                rating=None,
                ideal_caption=None,
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend service: {str(e)}")

# Display the generated caption and feedback form
if st.session_state.caption and not st.session_state.feedback_submitted:
    st.subheader("Generated Caption:")
    st.write(st.session_state.caption)

    st.subheader("Provide Feedback")
    score = st.slider("Rate the caption (1-10)", 1, 10, 5)
    user_caption = st.text_input("Please provide an accurate caption")

    # Submit feedback button
    if st.button("Submit Feedback"):
        log_manager.log_caption(
            image_id=st.session_state.image_id,
            generated_caption=st.session_state.caption,
            feedback_received=True,
            rating=score,
            ideal_caption=user_caption,
        )
        st.success("Thank you for your feedback!")
        st.session_state.feedback_submitted = True

# Option to upload another image after feedback is submitted
if st.session_state.feedback_submitted:
    if st.button("Upload Another Image"):
        reset_state()