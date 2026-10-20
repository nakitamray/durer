# Gets everything up to date and starts Durer: the API and the frontend each
# open in their own window. Safe to run after every git pull.
$root = $PSScriptRoot
$backend = Join-Path $root 'backend'
$frontend = Join-Path $root 'frontend'
$python = Join-Path $backend '.venv\Scripts\python.exe'

if (-not (Test-Path $python)) {
    Write-Host 'Making the Python environment (first run only)...'
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -3 -m venv (Join-Path $backend '.venv')
    } else {
        python -m venv (Join-Path $backend '.venv')
    }
}

Write-Host 'Checking Python packages...'
& $python -m pip install --quiet --disable-pip-version-check -r (Join-Path $backend 'requirements-dev.txt')
if ($LASTEXITCODE -ne 0) { Write-Host 'pip install failed, see above.' -ForegroundColor Red; exit 1 }

Write-Host 'Checking frontend packages...'
Push-Location $frontend
npm install --no-fund --no-audit --loglevel=error
$npmOk = $LASTEXITCODE -eq 0
Pop-Location
if (-not $npmOk) { Write-Host 'npm install failed, see above.' -ForegroundColor Red; exit 1 }

# python.exe straight from the venv, so nothing depends on activating it
Start-Process powershell -ArgumentList @(
    '-NoExit', '-Command',
    "Set-Location '$backend'; & '$python' -m uvicorn durer.main:app --reload --host 127.0.0.1 --port 8000"
)
Start-Process powershell -ArgumentList @(
    '-NoExit', '-Command',
    "Set-Location '$frontend'; npm run dev"
)

Write-Host ''
Write-Host 'Two windows should open. When the second one says ready, go to http://localhost:5173' -ForegroundColor Green
