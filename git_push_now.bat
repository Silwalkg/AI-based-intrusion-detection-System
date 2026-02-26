@echo off
setlocal

REM Set Git path
set GIT="C:\Program Files\Git\bin\git.exe"

echo ========================================
echo Pushing to GitHub Repository
echo https://github.com/Silwalkg/AI-powerd-IDS-System
echo ========================================
echo.

REM Check if Git exists
if not exist %GIT% (
    echo ERROR: Git not found at %GIT%
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo Git found. Proceeding...
echo.

REM Initialize Git if needed
if not exist ".git" (
    echo Step 1: Initializing Git repository...
    %GIT% init
    echo.
)

REM Configure Git
echo Step 2: Configuring Git...
%GIT% config user.name >nul 2>&1
if errorlevel 1 (
    %GIT% config --global user.name "Silwalkg"
)
%GIT% config user.email >nul 2>&1
if errorlevel 1 (
    %GIT% config --global user.email "silwalkg@example.com"
)
echo Git configured.
echo.

REM Add remote
echo Step 3: Setting up remote repository...
%GIT% remote get-url origin >nul 2>&1
if errorlevel 1 (
    %GIT% remote add origin https://github.com/Silwalkg/AI-powerd-IDS-System.git
    echo Remote added.
) else (
    %GIT% remote set-url origin https://github.com/Silwalkg/AI-powerd-IDS-System.git
    echo Remote updated.
)
echo.

REM Add all files
echo Step 4: Adding files...
%GIT% add .
echo Files added.
echo.

REM Commit
echo Step 5: Creating commit...
%GIT% commit -m "Update: Add comprehensive training guides and documentation"
if errorlevel 1 (
    echo No changes to commit or commit failed.
) else (
    echo Commit created.
)
echo.

REM Set main branch
echo Step 6: Setting main branch...
%GIT% branch -M main
echo.

REM Push
echo Step 7: Pushing to GitHub...
echo.
echo IMPORTANT: When prompted for credentials:
echo   Username: Silwalkg
echo   Password: Use your Personal Access Token (NOT password)
echo.
echo Create token at: https://github.com/settings/tokens
echo.
pause
echo.
echo Pushing now...
%GIT% push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo Push Failed!
    echo ========================================
    echo.
    echo Common issues:
    echo 1. Authentication failed - Use Personal Access Token
    echo 2. Repository access denied
    echo 3. Network connection issue
    echo.
    echo To create Personal Access Token:
    echo 1. Go to: https://github.com/settings/tokens
    echo 2. Click "Generate new token (classic)"
    echo 3. Select scope: repo (all)
    echo 4. Copy token and use as password
    echo.
) else (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Your code is now on GitHub:
    echo https://github.com/Silwalkg/AI-powerd-IDS-System
    echo.
)

pause
