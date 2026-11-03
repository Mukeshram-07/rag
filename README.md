# Restaurant Business Assistant

A local restaurant business knowledge assistant using Streamlit, ChromaDB, Ollama, and
`llama3.2`. Restaurant teams can upload menus, recipes, inventory reports, sales data,
supplier information, and operating procedures, then ask questions using natural language.

## Windows setup

Open PowerShell in this folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
ollama pull llama3.2
ollama pull nomic-embed-text
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the URL printed by Streamlit, upload one or more restaurant `.pdf`, `.xlsx`, or `.xlsm`
files, click **Index uploaded files**, and ask questions about the restaurant business.

Typical questions include:

- Which ingredients are needed for a menu item?
- What was the sales total for a specific day or month?
- Which products are low in stock?
- What is the approved recipe or preparation procedure?
- What are the supplier prices or ordering policies?

The Chroma database is stored locally in `data/chroma`. Uploaded files are kept in `uploads`. Both are ignored by Git.

## Configuration

Copy `.env.example` to `.env` to override:

- `OLLAMA_BASE_URL`: Ollama server URL, default `http://localhost:11434`
- `OLLAMA_CHAT_MODEL`: chat model, default `llama3.2`
- `OLLAMA_EMBED_MODEL`: embedding model, default `nomic-embed-text`
- `CHROMA_DIR`: persistent Chroma directory, default `./data/chroma`

## Troubleshooting

- Check Ollama is running with `ollama list`.
- If answers say no restaurant documents are indexed, index the uploaded files from the sidebar.
- If embedding fails, run `ollama pull nomic-embed-text`.
