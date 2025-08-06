import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from io import BytesIO

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key, timeout=120)

# Session state init
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None
if "vector_store_map" not in st.session_state:
    st.session_state.vector_store_map = {}  # file_id -> vector_store_id
if "selected_vs_ids" not in st.session_state:
    st.session_state.selected_vs_ids = []

# Helper functions
def list_assistants():
    return {a.id: a.name for a in client.beta.assistants.list().data}

def list_files():
    return {f.id: f.filename for f in client.files.list().data}

def create_vector_store_for_file(file_id, filename):
    vs = client.vector_stores.create(
        name=filename,
        file_ids=[file_id]
    )
    return vs.id

def delete_vector_store(vs_id):
    client.vector_stores.delete(vector_store_id=vs_id)

# UI
st.title("📄 Chat with your PDF")

# 1) Assistant selection/creation
st.subheader("🦾 Assistant")
assts = list_assistants()
options = [f"{n} ({i})" for i, n in assts.items()] + ["Create New Assistant"]
choice = st.selectbox("Choose Assistant:", options)
if choice == "Create New Assistant" and st.button("➕ Create Assistant"):
    new = client.beta.assistants.create(
        name="PDF Assistant",
        instructions="Answer only from uploaded PDFs.",
        model="gpt-4o",
        tools=[{"type": "file_search"}]
    )
    st.session_state.assistant_id = new.id
    st.success(f"Created assistant {new.name} ({new.id})")
elif choice != "Create New Assistant":
    aid = choice.split("(")[-1].strip(")")
    st.session_state.assistant_id = aid
    st.success(f"Using assistant {assts[aid]} ({aid})")

# 2) Upload & manage files/vector stores
st.subheader("📂 Files & Vector Stores")
files = list_files()
# existing files selection
for file_id, name in files.items():
    checked = file_id in st.session_state.selected_vs_ids
    toggle = st.checkbox(f"{name} ({file_id})", value=checked, key=file_id)
    if toggle and file_id not in st.session_state.selected_vs_ids:
        if file_id not in st.session_state.vector_store_map:
            vsid = create_vector_store_for_file(file_id, name)
            st.session_state.vector_store_map[file_id] = vsid
        st.session_state.selected_vs_ids.append(file_id)
    if not toggle and file_id in st.session_state.selected_vs_ids:
        st.session_state.selected_vs_ids.remove(file_id)

# upload new PDF
upload = st.file_uploader("Upload new PDF", type=["pdf"])
if upload and st.button("📤 Upload & Build Store"):
    f = client.files.create(file=upload, purpose="assistants")
    vsid = create_vector_store_for_file(f.id, f.filename)
    st.session_state.vector_store_map[f.id] = vsid
    st.session_state.selected_vs_ids.append(f.id)
    st.success(f"Uploaded {f.filename}, vector store {vsid}")

# delete selected
if st.button("🗑️ Delete Selected Files & Stores"):
    for fid in list(st.session_state.selected_vs_ids):
        vsid = st.session_state.vector_store_map.pop(fid, None)
        if vsid:
            delete_vector_store(vsid)
        client.files.delete(file_id=fid)
    st.session_state.selected_vs_ids = []
    st.success("Deleted selected files and their vector stores.")

# 3) Ask question
st.subheader("💬 Ask a question")
query = st.text_input("Your question:")
if st.button("Ask") and query and st.session_state.assistant_id:
    vs_ids = list(st.session_state.vector_store_map.values())
    if not vs_ids:
        st.error("Please upload or select at least one PDF first.")
    else:
        thread = client.beta.threads.create(
            tool_resources={"file_search": {"vector_store_ids": vs_ids}},
            messages=[{"role": "user", "content": query}]
        )
        client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=st.session_state.assistant_id
        )
        msgs = client.beta.threads.messages.list(thread_id=thread.id).data
        for m in reversed(msgs):
            if m.role == "assistant":
                st.markdown("### 🤖 Assistant Response")
                st.write(m.content[0].text.value)
                break