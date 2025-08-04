import streamlit as st
from openai import OpenAI
import os

# Set your OpenAI API key
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""),
                timeout=120)

# Set session state variables for assistant, thread, and uploaded files
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "file_ids" not in st.session_state:
    st.session_state.file_ids = []

st.title("📄 Chat with your PDF")

# File upload (only PDF for now)
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    # Upload to OpenAI
    with st.spinner("Uploading to OpenAI..."):
        file = client.files.create(file=uploaded_file, purpose="assistants")
        st.session_state.file_ids.append(file.id)
        st.success("Uploaded and attached to assistant.")

# Create assistant if not created
if st.session_state.assistant_id is None and st.session_state.file_ids:
    with st.spinner("Creating assistant..."):
        assistant = client.beta.assistants.create(
            name="PDF Assistant",
            instructions="You are a helpful assistant. Answer questions based only on the uploaded documents.",
            model="gpt-4o",
            tools=[{"type": "file_search"}]
        )
        st.session_state.assistant_id = assistant.id
        st.success("Assistant created!")

# Create thread if not created
if st.session_state.thread_id is None and st.session_state.assistant_id:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

# Chat interface
st.subheader("💬 Ask a question about the PDF")

user_input = st.text_input("Your question:", placeholder="e.g. Summarize this document...")
if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):
        # Send message
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input,
            attachments=[
                {"file_id": file_id, "tools": [{"type": "file_search"}]}
                for file_id in st.session_state.file_ids
            ]
        )

        # Run assistant and wait for response
        run = client.beta.threads.runs.create_and_poll(
            thread_id=st.session_state.thread_id,
            assistant_id=st.session_state.assistant_id
        )

        # Get and display latest message
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                st.markdown("### 🤖 Assistant Response")
                st.write(msg.content[0].text.value)
                break
