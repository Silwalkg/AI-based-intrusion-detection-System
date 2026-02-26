@echo off
echo ========================================
echo GitHub Setup for IDS Project
echo ========================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo Git is installed. Proceeding...
echo.

REM Initialize Git repository
echo Step 1: Initializing Git repository...
git init
echo.

REM Add all files
echo Step 2: Adding files to Git...
git add .
echo.

REM Create first commit
echo Step 3: Creating initial commit...
git commit -m "Initial commit: AI-Powered Intrusion Detection System with training guides"
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Create a new repository on GitHub: https://github.com/new
echo 2. Name it: intrusion-detection-system
echo 3. Run these commands:
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/intrusion-detection-system.git
echo    git branch -M main
echo    git push -u origin main
echo.
pause
