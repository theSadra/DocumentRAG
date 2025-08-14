import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

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

# Auto-initialize vector_store_map with existing vector stores from OpenAI
if not st.session_state.vector_store_map:
    # Load vector stores
    # Get all files: id -> filename
    files = {f.id: f.filename for f in client.files.list().data}

    # Get all vector stores
    vector_stores = client.vector_stores.list().data

    # Map file_id -> vector_store_id by matching vector_store.name to filename
    for vs in vector_stores:
        for fid, fname in files.items():
            if vs.name == fname:
                st.session_state.vector_store_map[fid] = vs.id
                break

# Helper functions
def list_assistants():
    return {a.id: a.name for a in client.beta.assistants.list().data}

def list_files():
    return {f.id: f.filename for f in client.files.list().data}

def create_vector_store_for_file(file_id, filename):
    vs = client.vector_stores.create(name=filename, file_ids=[file_id])
    return vs.id

def delete_vector_store(vs_id):
    client.vector_stores.delete(vector_store_id=vs_id)

def update_assistant_vs(assistant_id, vs_ids):
    client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": vs_ids}}
    )

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

# 3) Ask question and update assistant vector store
st.subheader("💬 Ask a question")

# Let the user select a file for querying and assistant update
if st.session_state.vector_store_map:
    file_choices = {
        fid: f"{list_files().get(fid, 'Unknown file')} ({fid})"
        for fid in st.session_state.vector_store_map.keys()
    }

    selected_fid = st.selectbox(
        "Choose a file to use and ask about:",
        options=list(file_choices.keys()),
        format_func=lambda x: file_choices[x]
    )
    vsid = st.session_state.vector_store_map[selected_fid]

    if st.button("Update Assistant with Selected File"):
        update_assistant_vs(st.session_state.assistant_id, [vsid])
        st.success(f"Assistant updated with vector store {vsid} for file {file_choices[selected_fid]}")

    query = st.text_input("Your question:")
    if st.button("Ask") and query and st.session_state.assistant_id:
        thread = client.beta.threads.create(
            tool_resources={"file_search": {"vector_store_ids": [vsid]}},
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
else:
    st.warning("Please upload a PDF and build a vector store before asking a question.")
