# ========================================================
# Script PowerShell khởi chạy toàn bộ Retail Intelligence Platform
# Sử dụng: Mở PowerShell và gõ: .\run_system.ps1
# ========================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " KHOI DONG RETAIL INTELLIGENCE PLATFORM (POWERSHELL)      " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$PROJECT_DIR = $PSScriptRoot
Set-Location $PROJECT_DIR

# 1. Kiem tra Docker (Tuy chon)
Write-Host "`n[1/3] Kiem tra trang thai Docker..." -ForegroundColor Yellow
try {
    $dockerCheck = docker ps 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "-> Docker dang hoat dong. Dang khoi dong cac container ha tang..." -ForegroundColor Green
        docker compose up -d
    } else {
        Write-Host "-> Docker Desktop chua bat. He thong se tu dong chay che do Fallback (Local Store)!" -ForegroundColor DarkYellow
    }
} catch {
    Write-Host "-> Khong tim thay Docker CLI. He thong van hoat dong qua co che Fallback." -ForegroundColor DarkYellow
}

# 2. Khoi dong FastAPI Backend tren cua so moi
Write-Host "`n[2/3] Dang khoi dong FastAPI Backend (Port 8000)..." -ForegroundColor Yellow
$fastapiCmd = "cd '$PROJECT_DIR'; .\.venv\Scripts\Activate.ps1; python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$fastapiCmd"
Start-Sleep -Seconds 2

# 3. Khoi dong Streamlit Dashboard Portal
Write-Host "`n[3/3] Dang khoi dong Streamlit Dashboard Portal (Port 8501)..." -ForegroundColor Yellow
$streamlitCmd = "cd '$PROJECT_DIR'; .\.venv\Scripts\Activate.ps1; python -m streamlit run dashboard/app.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$streamlitCmd"

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " HE THONG DA DUOC KHOI DONG THANH CONG!                   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "• Streamlit Dashboard : http://localhost:8501" -ForegroundColor White
Write-Host "• FastAPI Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "`n* Luu y: De mo phong phat don hang Real-time (Kafka), mo them 1 cua so va chay:" -ForegroundColor Gray
Write-Host "  python streaming/producer.py" -ForegroundColor Cyan
