@echo off
REM Startup script for QA Agent (Windows)

echo ========================================
echo 🚀 Starting QA Agent
echo Test Case ^& Script Generator
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo ⚠️  Please edit .env file and add your AWS credentials:
    echo    - AWS_ACCESS_KEY_ID
    echo    - AWS_SECRET_ACCESS_KEY
    echo    - AWS_REGION
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo ========================================
echo Starting services...
echo ========================================
echo.

REM Start backend
echo 🔷 Starting FastAPI Backend on http://localhost:8000
start "QA Agent Backend" /MIN cmd /c "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload > logs\backend.log 2>&1"

REM Wait for backend to be ready
timeout /t 3 /nobreak > nul
echo    ✓ Backend started
echo    📚 API Docs: http://localhost:8000/docs
echo.

REM Start frontend
echo 🔶 Starting Streamlit Frontend on http://localhost:8501
start "QA Agent Frontend" /MIN cmd /c "streamlit run frontend\streamlit_app.py > logs\frontend.log 2>&1"

timeout /t 2 /nobreak > nul
echo    ✓ Frontend started
echo.

echo ========================================
echo ✅ QA Agent is now running!
echo ========================================
echo.
echo 🌐 Access the application:
echo    Streamlit UI:  http://localhost:8501
echo    FastAPI Docs:  http://localhost:8000/docs
echo    Health Check:  http://localhost:8000/health
echo.
echo 📋 Check logs in the logs\ directory
echo.
echo Press any key to stop all services...
echo ========================================

pause > nul

echo.
echo 🛑 Shutting down services...
taskkill /FI "WINDOWTITLE eq QA Agent Backend" /F > nul 2>&1
taskkill /FI "WINDOWTITLE eq QA Agent Frontend" /F > nul 2>&1

echo ✅ Services stopped
pause
