@echo off
echo 🚀 Starting Raphael AI Development Environment
echo ============================================

echo.
echo 📋 Checking prerequisites...

REM Check if Firebase CLI is installed
firebase --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Firebase CLI not found. Installing...
    npm install -g firebase-tools
) else (
    echo ✅ Firebase CLI found
)

REM Check if Python dependencies are installed
echo.
echo 📦 Checking Python dependencies...
cd functions
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo 📥 Installing Python dependencies...
    pip install -r requirements.txt
) else (
    echo ✅ Python dependencies installed
)

REM Check if Node dependencies are installed
echo.
echo 📦 Checking Node dependencies...
cd ..\public
if not exist node_modules (
    echo 📥 Installing Node dependencies...
    npm install
) else (
    echo ✅ Node dependencies installed
)

REM Check for environment file
cd ..\functions
if not exist .env (
    echo.
    echo ⚠️  Environment file not found!
    echo 📝 Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo 🔑 Please edit functions\.env and add your API keys:
    echo    - GEMINI_API_KEY (from https://makersuite.google.com/app/apikey)
    echo.
    pause
) else (
    echo ✅ Environment file found
)

echo.
echo 🚀 Starting Firebase emulators...
cd ..
firebase emulators:start

pause
