Write-Host "Starting Instagram Shop Automation Backend..." -ForegroundColor Green
Set-Location $PSScriptRoot
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload 