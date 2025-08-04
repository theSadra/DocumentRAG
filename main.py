import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF
from io import BytesIO
#
# Load environment  variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key, timeout=120)

# Session state for app
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "file_ids" not in st.session_state:
    st.session_state.file_ids = []
if "pdf_file" not in st.session_state:
    st.session_state.pdf_file = None
if "uploaded_to_openai" not in st.session_state:
    st.session_state.uploaded_to_openai = False

st.title("📄 Chat with your PDF")

# Step 1: Upload PDF
uploaded_file = st.file_uploader("Choose a PDF to preview and use", type=["pdf"])

if uploaded_file:
    st.session_state.pdf_file = uploaded_file
    st.session_state.uploaded_to_openai = False  # Reset state on new upload

    # Show first page preview
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    first_page = doc.load_page(0)
    pix = first_page.get_pixmap()
    img_bytes = BytesIO(pix.tobytes("png"))
    st.image(img_bytes, caption="First Page Preview", use_container_width=True)

    # Reset file position for re-upload
    uploaded_file.seek(0)

    # Upload button
    if st.button("📤 Upload to OpenAI"):
        with st.spinner("Uploading to OpenAI..."):
            file = client.files.create(file=uploaded_file, purpose="assistants")
            st.session_state.file_ids = [file.id]
            st.session_state.uploaded_to_openai = True
        st.success("File uploaded and ready for assistant.")

# Step 2: Create assistant (after OpenAI upload)
if st.session_state.uploaded_to_openai and st.session_state.assistant_id is None:
    with st.spinner("Creating assistant..."):
        assistant = client.beta.assistants.create(
            name="PDF Assistant",
            instructions="You are a helpful assistant. Answer questions based only on the uploaded documents.",
            model="gpt-4o",
            tools=[{"type": "file_search"}]
        )
        st.session_state.assistant_id = assistant.id
    st.success("Assistant created!")

# Step 3: Ask question
st.subheader("💬 Ask a question about the PDF")
user_input = st.text_input("Your question:", placeholder="e.g. Summarize this document...", key="user_question")

if st.button("Ask") and user_input and st.session_state.file_ids:
    with st.spinner("Thinking..."):
        # Create a new thread for each question to avoid previous context
        st.session_state.thread_id = None
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

        # Send user message
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input,
            attachments=[
                {"file_id": file_id, "tools": [{"type": "file_search"}]}
                for file_id in st.session_state.file_ids
            ]
        )

        # Run assistant
        run = client.beta.threads.runs.create_and_poll(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id
        )

        # Get response
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                st.markdown("### 🤖 Assistant Response")
                st.write(msg.content[0].text.value)
                break