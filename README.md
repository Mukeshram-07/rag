# Local RAG Chatbot

A local PDF/Excel question-answering app using Streamlit, ChromaDB, Ollama, and `llama3.2`.

## Windows setup

Open PowerShell in this folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
ollama pull llama3.2
ollama pull nomic-embed-text
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the URL printed by Streamlit, upload one or more `.pdf`, `.xlsx`, or `.xlsm` files, click **Index uploaded files**, and start chatting.

The Chroma database is stored locally in `data/chroma`. Uploaded files are kept in `uploads`. Both are ignored by Git.

## Configuration

Copy `.env.example` to `.env` to override:

- `OLLAMA_BASE_URL`: Ollama server URL, default `http://localhost:11434`
- `OLLAMA_CHAT_MODEL`: chat model, default `llama3.2`
- `OLLAMA_EMBED_MODEL`: embedding model, default `nomic-embed-text`
- `CHROMA_DIR`: persistent Chroma directory, default `./data/chroma`

## Troubleshooting

- Check Ollama is running with `ollama list`.
- If answers say no documents are indexed, index the uploaded files from the sidebar.
- If embedding fails, run `ollama pull nomic-embed-text`.
