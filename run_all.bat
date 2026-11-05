@echo off
chcp 65001 > nul
title Retail Intelligence Platform Launcher
echo ==========================================================
echo  KHỞI ĐỘNG RETAIL INTELLIGENCE PLATFORM (WINDOWS)
echo ==========================================================
cd /d "%~dp0"

echo [1/3] Kiểm tra Docker...
docker compose up -d 2>nul
if %errorlevel% neq 0 (
    echo [!] Docker chưa bật. Hệ thống sẽ tự động dùng chế độ Fallback Local Store.
)

echo [2/3] Đang khởi động FastAPI Backend (Port 8000)...
start "FastAPI Backend" cmd /k "call .venv\Scripts\activate.bat && python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak > nul

echo [3/3] Đang khởi động Streamlit Dashboard (Port 8501)...
start "Streamlit Portal" cmd /k "call .venv\Scripts\activate.bat && python -m streamlit run dashboard/app.py"

echo.
echo ==========================================================
echo  HỆ THỐNG ĐÃ SẴN SÀNG!
echo ==========================================================
echo • Streamlit Dashboard : http://localhost:8501
echo • FastAPI Swagger Docs: http://127.0.0.1:8000/docs
echo.
echo Để mô phỏng đơn hàng Real-time, mở thêm 1 cửa sổ và chạy:
echo   python streaming/producer.py
echo.
pause
