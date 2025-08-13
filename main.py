import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Config / Client Setup
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key, timeout=120)

# Session state init
if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None
if "vector_store_map" not in st.session_state:
    # optional local mapping file_id -> vector_store_id for stores this UI created
    st.session_state.vector_store_map = {}
if "files_selected" not in st.session_state:
    st.session_state.files_selected = []
if "vs_selected_for_deletion" not in st.session_state:
    st.session_state.vs_selected_for_deletion = []
if "merged_vector_stores" not in st.session_state:
    st.session_state.merged_vector_stores = {}
if "current_vs_id" not in st.session_state:
    st.session_state.current_vs_id = None

# Helper functions
def list_assistants():
    return {a.id: a.name for a in client.beta.assistants.list().data}

def list_files():
    return {f.id: f.filename for f in client.files.list().data}

def list_vector_stores():
    return client.vector_stores.list().data

def create_vector_store_for_file(file_id, filename):
    vs = client.vector_stores.create(name=filename, file_ids=[file_id])
    return getattr(vs, "id", None) or (vs.get("id") if isinstance(vs, dict) else None)

def delete_vector_store(vs_id):
    client.vector_stores.delete(vector_store_id=vs_id)

def create_merged_vector_store(file_ids, name=None):
    # If no name provided, create a simple unique incremental name without timestamp.
    if not name:
        base = "merged_store"
        existing_names = {safe_get_attr(vs, "name") or safe_get_attr(vs, "id") for vs in list_vector_stores()}
        candidate = base
        i = 2
        while candidate in existing_names:
            candidate = f"{base}_{i}"
            i += 1
        name = candidate
    vs = client.vector_stores.create(name=name, file_ids=file_ids)
    return getattr(vs, "id", None) or (vs.get("id") if isinstance(vs, dict) else None)

def find_vector_stores_for_file(file_id, vs_list):
    vs_ids = []
    for vs in vs_list:
        file_ids = getattr(vs, "file_ids", None)
        if file_ids is None and isinstance(vs, dict):
            file_ids = vs.get("file_ids", [])
        if file_ids and file_id in file_ids:
            vs_id = getattr(vs, "id", None) or (vs.get("id") if isinstance(vs, dict) else None)
            if vs_id:
                vs_ids.append(vs_id)
    return vs_ids

def safe_get_attr(obj, key):
    return getattr(obj, key, None) if not isinstance(obj, dict) else obj.get(key)

# UI
st.title("📄 Chat with your PDF")

# Create tabs for a clearer, more logical layout
files_tab, vs_tab, assistant_tab, chat_tab = st.tabs(["📂 Files", "🧭 Vector Stores", "🦾 Assistant", "💬 Chat"])

with files_tab:
    st.subheader("Upload & Manage Files")
    files = list_files()
    # Simplify layout: uploader full width, then actions row
    upload = st.file_uploader("Select PDF file(s) to upload", type=["pdf"], accept_multiple_files=True, help="You can select one or multiple PDFs.")
    c1, c2 = st.columns([1,3])
    with c1:
        upload_clicked = st.button("📤 Upload", use_container_width=True, disabled=not upload)
    with c2:
        auto_vs = st.toggle("Automatically create a vector store for each uploaded file", value=False, help="If enabled, each file will immediately get its own vector store.")
    if upload_clicked and upload:
        uploads = upload if isinstance(upload, list) else [upload]
        created_vs_count = 0
        for up in uploads:
            f = client.files.create(file=up, purpose="assistants")
            st.success(f"Uploaded {f.filename} ({f.id}).")
            if auto_vs:
                vsid = create_vector_store_for_file(f.id, f.filename)
                st.session_state.vector_store_map[f.id] = vsid
                created_vs_count += 1
                st.info(f"Created vector store {vsid} for {f.filename}")
        if auto_vs and created_vs_count:
            st.success(f"Created {created_vs_count} vector store(s).")
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("Stored Files")
    if not files:
        st.info("No files in storage.")
    else:
        st.write("Select files (for creating vector stores, deletion, or merge).")
        for file_id, name in files.items():
            key = f"file_cb_{file_id}"
            checked = file_id in st.session_state.files_selected
            toggle = st.checkbox(f"{name} ({file_id})", value=checked, key=key)
            if toggle and file_id not in st.session_state.files_selected:
                st.session_state.files_selected.append(file_id)
            if not toggle and file_id in st.session_state.files_selected:
                st.session_state.files_selected.remove(file_id)
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if st.button("🛠️ Create Vector Store for Selected Files", help="Creates one vector store per selected file"):
                if not st.session_state.files_selected:
                    st.info("No files selected.")
                else:
                    for fid in list(st.session_state.files_selected):
                        filename = list_files().get(fid, fid)
                        vsid = create_vector_store_for_file(fid, filename)
                        st.session_state.vector_store_map[fid] = vsid
                        st.success(f"Created vector store {vsid} for file {fid}")
        with col_f2:
            if st.button("🗑️ Delete Selected Files", help="Also deletes any vector stores containing these files"):
                if not st.session_state.files_selected:
                    st.info("No files selected for deletion.")
                else:
                    vs_list = list_vector_stores()
                    deleted_any = False
                    for fid in list(st.session_state.files_selected):
                        vs_for_file = find_vector_stores_for_file(fid, vs_list)
                        for vsid in vs_for_file:
                            delete_vector_store(vsid)
                            deleted_any = True
                            # clean local map if present
                            for k, v in list(st.session_state.vector_store_map.items()):
                                if v == vsid:
                                    st.session_state.vector_store_map.pop(k, None)
                        client.files.delete(file_id=fid)
                        deleted_any = True
                        if fid in st.session_state.files_selected:
                            st.session_state.files_selected.remove(fid)
                    if deleted_any:
                        st.success("Deleted selected files and related vector stores.")

    st.markdown("---")
    st.subheader("Merge Selected Files into One Vector Store")
    if len(st.session_state.files_selected) < 2:
        st.info("Select two or more files above to merge.")
    merge_name = st.text_input("Merged store name (blank = automatic):", value="", placeholder="e.g. project_docs")
    if st.button("🔗 Create merged vector store from selected files", key="merge_btn_files_tab"):
        file_ids = list(st.session_state.files_selected)
        if not file_ids:
            st.info("No files selected to merge.")
        else:
            merged_vs = create_merged_vector_store(file_ids, name=merge_name.strip() or None)
            # Store metadata with resolved name (fetch it back to display accurate chosen/auto name)
            vs_obj = next((v for v in list_vector_stores() if safe_get_attr(v, "id") == merged_vs), None)
            resolved_name = safe_get_attr(vs_obj, "name") or merge_name.strip() or "merged_store"
            st.session_state.merged_vector_stores[merged_vs] = {"name": resolved_name, "file_ids": file_ids}
            st.session_state.current_vs_id = merged_vs
            st.success(f"Created merged vector store '{resolved_name}' ({merged_vs}) and set active.")

with vs_tab:
    st.subheader("Vector Stores")
    all_vs = list_vector_stores()
    if not all_vs:
        st.info("No vector stores found.")
    else:
        vs_label_map = {}
        for vs in all_vs:
            vs_id = safe_get_attr(vs, "id")
            vs_name = safe_get_attr(vs, "name") or vs_id
            file_ids = safe_get_attr(vs, "file_ids") or []
            file_ids_str = ", ".join(map(str, file_ids)) if file_ids else ""
            label = f"{vs_name} ({vs_id})" + (f" - files: [{file_ids_str}]" if file_ids_str else "")
            vs_label_map[vs_id] = label
        labels = list(vs_label_map.values())
        label_to_vsid = {v: k for k, v in vs_label_map.items()}
        default_index = 0
        if st.session_state.current_vs_id in vs_label_map:
            default_label = vs_label_map[st.session_state.current_vs_id]
            if default_label in labels:
                default_index = labels.index(default_label)
        chosen_label = st.selectbox("Select active vector store for chat:", labels, index=default_index)
        st.session_state.current_vs_id = label_to_vsid.get(chosen_label)
        st.markdown(f"*Active vector store:* `{st.session_state.current_vs_id}`")

        st.markdown("---")
        st.write("Mark vector stores for deletion:")
        for vs in all_vs:
            vs_id = safe_get_attr(vs, "id")
            label = vs_label_map.get(vs_id, vs_id)
            key = f"vs_cb_{vs_id}"
            checked = vs_id in st.session_state.vs_selected_for_deletion
            toggle = st.checkbox(label, value=checked, key=key)
            if toggle and vs_id not in st.session_state.vs_selected_for_deletion:
                st.session_state.vs_selected_for_deletion.append(vs_id)
            if not toggle and vs_id in st.session_state.vs_selected_for_deletion:
                st.session_state.vs_selected_for_deletion.remove(vs_id)
        if st.button("🗑️ Delete Selected Vector Stores"):
            if not st.session_state.vs_selected_for_deletion:
                st.info("No vector stores selected.")
            else:
                for vsid in list(st.session_state.vs_selected_for_deletion):
                    delete_vector_store(vsid)
                    for fid, mapped in list(st.session_state.vector_store_map.items()):
                        if mapped == vsid:
                            st.session_state.vector_store_map.pop(fid, None)
                    if st.session_state.current_vs_id == vsid:
                        st.session_state.current_vs_id = None
                    st.session_state.vs_selected_for_deletion.remove(vsid)
                    st.success(f"Deleted vector store {vsid}")

with assistant_tab:
    st.subheader("Assistants")
    assts = list_assistants()
    assistant_options = [f"{n} ({i})" for i, n in assts.items()] + ["Create New Assistant"]
    choice = st.selectbox("Choose Assistant:", assistant_options, key="assistant_select")
    if choice == "Create New Assistant":
        if st.button("➕ Create Assistant"):
            new = client.beta.assistants.create(
                name="PDF Assistant",
                instructions="Answer only from uploaded PDFs.",
                model="gpt-4o",
                tools=[{"type": "file_search"}],
            )
            st.session_state.assistant_id = new.id
            st.success(f"Created assistant {new.name} ({new.id})")
    else:
        aid = choice.split("(")[-1].strip(")")
        st.session_state.assistant_id = aid
        st.success(f"Using assistant {assts.get(aid, aid)} ({aid})")
    st.markdown(f"Current assistant: `{st.session_state.assistant_id or 'None'}`")

with chat_tab:
    st.subheader("Ask a Question")
    if not st.session_state.assistant_id:
        st.warning("Select or create an assistant in the Assistant tab.")
    if not st.session_state.current_vs_id:
        st.warning("Select or create a vector store in the Vector Stores tab.")
    query = st.text_input("Your question:")
    if st.button("Ask", key="ask_btn") and query:
        if not st.session_state.assistant_id:
            st.error("No assistant selected.")
        elif not st.session_state.current_vs_id:
            st.error("No vector store selected.")
        else:
            thread = client.beta.threads.create(
                tool_resources={"file_search": {"vector_store_ids": [st.session_state.current_vs_id]}},
                messages=[{"role": "user", "content": query}],
            )
            client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=st.session_state.assistant_id)
            msgs = client.beta.threads.messages.list(thread_id=thread.id).data
            for m in reversed(msgs):
                role = safe_get_attr(m, "role") or (m.get("role") if isinstance(m, dict) else None)
                if role == "assistant":
                    content = safe_get_attr(m, "content") or (m.get("content") if isinstance(m, dict) else None)
                    if isinstance(content, list) and len(content) > 0:
                        first = content[0]
                        text_obj = safe_get_attr(first, "text") or (first.get("text") if isinstance(first, dict) else None)
                        if text_obj is not None:
                            if hasattr(text_obj, "value"):
                                st.markdown("### 🤖 Assistant Response")
                                st.write(text_obj.value)
                                break
                            if isinstance(text_obj, dict) and "value" in text_obj:
                                st.markdown("### 🤖 Assistant Response")
                                st.write(text_obj["value"])
                                break
                        st.markdown("### 🤖 Assistant Response")
                        st.write(content)
                        break
                    else:
                        st.markdown("### 🤖 Assistant Response")
                        st.write(content)
                        break

st.markdown("---")
st.caption("Behavior: Upload adds files. You must create vector stores (one per file or merged) to query. Select an assistant and vector store before chatting.")