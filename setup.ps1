$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete."
Write-Host "1. Copy .env.example to .env."
Write-Host "2. Set OLLAMA_API_KEY to your Ollama Cloud API key."
Write-Host "3. Start the app: .\.venv\Scripts\python.exe -m streamlit run app.py"
