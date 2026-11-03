$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete."
Write-Host "1. Install Ollama from https://ollama.com/download"
Write-Host "2. Run: ollama pull llama3.2"
Write-Host "3. Run: ollama pull nomic-embed-text"
Write-Host "4. Start the app: .\.venv\Scripts\python.exe -m streamlit run app.py"
