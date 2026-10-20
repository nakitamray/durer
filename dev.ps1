# Starts the API and the frontend in two windows. Run the setup in the README once first.
$root = $PSScriptRoot

Start-Process powershell -ArgumentList @(
    '-NoExit', '-Command',
    "Set-Location '$root\backend'; .\.venv\Scripts\Activate.ps1; uvicorn durer.main:app --reload"
)
Start-Process powershell -ArgumentList @(
    '-NoExit', '-Command',
    "Set-Location '$root\frontend'; npm run dev"
)

Write-Host "API on http://localhost:8000, app on http://localhost:5173"
