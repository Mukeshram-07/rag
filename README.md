# Restaurant Business Assistant

A restaurant business knowledge assistant using Streamlit, ChromaDB, Ollama Cloud, and
`gemma4:31b` through Ollama Cloud. Chroma uses a lightweight local retrieval embedding model;
no local chat LLM is required. Restaurant teams can upload menus, recipes, inventory reports, sales data,
supplier information, and operating procedures, then ask questions using natural language.

## Windows setup

Open PowerShell in this folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
.\.venv\Scripts\python.exe -m streamlit run app.py
```

For local Windows use, copy `.env.example` to `.env` and set `OLLAMA_API_KEY` to your Ollama
Cloud API key. The app uses `https://ollama.com` for chat with `gemma4:31b`; Chroma downloads
its lightweight retrieval embedding model automatically. No local Ollama installation is required.

For Streamlit Cloud, open **Settings > Secrets** and paste valid TOML. The app reads these
values from `st.secrets`; do not paste the `KEY=value` format from `.env.example`:

```toml
OLLAMA_BASE_URL = "https://ollama.com"
OLLAMA_API_KEY = "your-ollama-cloud-api-key"
OLLAMA_MODEL = "gemma4:31b"
CHROMA_DIR = "./data/chroma"
```

See [.streamlit/secrets.toml.example](.streamlit/secrets.toml.example) for a template.

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

- `OLLAMA_BASE_URL`: Ollama Cloud URL, default `https://ollama.com`
- `OLLAMA_API_KEY`: Ollama Cloud API key
- `OLLAMA_MODEL`: Ollama Cloud chat model, default `gemma4:31b`
- `CHROMA_DIR`: persistent Chroma directory, default `./data/chroma`

## Troubleshooting

- Check that `OLLAMA_API_KEY` is set and valid for Ollama Cloud.
- If answers say no restaurant documents are indexed, index the uploaded files from the sidebar.
- On first indexing, Chroma downloads its retrieval embedding model. Ensure the deployment
  has outbound internet access.
