from pathlib import Path

import streamlit as st

from rag import RAGEngine

st.set_page_config(page_title="Restaurant Business Assistant", page_icon="🍽️", layout="wide")


@st.cache_resource
def get_engine() -> RAGEngine:
    return RAGEngine()


engine = get_engine()
st.title("🍽️ Restaurant Business Assistant")
st.caption(
    "Ask questions about menus, recipes, inventory, sales, operations, and restaurant policies "
    "using Ollama Cloud."
)

with st.sidebar:
    st.header("Restaurant knowledge base")
    uploaded_files = st.file_uploader(
        "Upload restaurant PDFs or Excel files",
        type=["pdf", "xlsx", "xlsm"],
        accept_multiple_files=True,
    )
    if st.button("Index uploaded files", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("Choose at least one restaurant PDF or Excel file.")
        else:
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            total = 0
            with st.status("Indexing files...", expanded=True) as status:
                for uploaded in uploaded_files:
                    target = upload_dir / uploaded.name
                    target.write_bytes(uploaded.getvalue())
                    count = engine.index_file(target)
                    total += count
                    st.write(f"{uploaded.name}: {count} chunks")
                status.update(label=f"Indexed {total} chunks", state="complete")
    if st.button("Clear knowledge base", use_container_width=True):
        engine.clear()
        st.session_state.messages = []
        st.success("Knowledge base cleared.")
    st.divider()
    st.subheader("Indexed restaurant files")
    files = engine.indexed_files()
    st.write(files if files else "No files indexed yet.")
    st.caption("Ollama Cloud model: gemma4:31b-cloud")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Ask about menus, inventory, sales, recipes, or restaurant operations..."
)
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching your knowledge base..."):
                answer, sources = engine.answer(
                    question,
                    st.session_state.messages[:-1],
                )
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.sources = sources
        except Exception as error:
            st.error(str(error))

if st.session_state.sources:
    with st.expander("Retrieved sources"):
        for index, source in enumerate(st.session_state.sources, start=1):
            st.markdown(f"**[{index}] {source['source']} — {source['location']}**")
            st.caption(source["text"])
