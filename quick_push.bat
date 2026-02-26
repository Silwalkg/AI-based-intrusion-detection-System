@echo off
echo ========================================
echo Quick Push to GitHub
echo ========================================
echo.

REM Test if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not recognized!
    echo.
    echo Please RESTART your terminal first!
    echo.
    echo Steps:
    echo 1. Close this window
    echo 2. Open a NEW terminal/PowerShell
    echo 3. Navigate to: cd "D:\Intrution Detection System\Intrution Detection System"
    echo 4. Run: quick_push.bat
    echo.
    pause
    exit /b 1
)

echo Git is available! Version:
git --version
echo.

REM Initialize if needed
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo.
)

REM Configure
echo Configuring Git...
git config --global user.name "Silwalkg"
git config --global user.email "silwalkg@example.com"
echo.

REM Add remote
echo Setting up remote...
git remote remove origin 2>nul
git remote add origin https://github.com/Silwalkg/AI-powerd-IDS-System.git
echo.

REM Add files
echo Adding files...
git add .
echo.

REM Commit
echo Creating commit...
git commit -m "Update: Add comprehensive training guides and documentation"
echo.

REM Push
echo Setting main branch...
git branch -M main
echo.

echo ========================================
echo Ready to push to GitHub!
echo ========================================
echo.
echo Repository: https://github.com/Silwalkg/AI-powerd-IDS-System
echo.
echo When prompted:
echo   Username: Silwalkg
echo   Password: [Your Personal Access Token]
echo.
echo Create token at: https://github.com/settings/tokens
echo.
pause

echo Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo Push Failed!
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. Wrong credentials - Use Personal Access Token
    echo 2. Network issue
    echo 3. Repository access denied
    echo.
    echo Try again or push manually with:
    echo   git push -u origin main
    echo.
) else (
    echo.
    echo ========================================
    echo SUCCESS! ✓
    echo ========================================
    echo.
    echo Your code is now on GitHub!
    echo View at: https://github.com/Silwalkg/AI-powerd-IDS-System
    echo.
)

pause
