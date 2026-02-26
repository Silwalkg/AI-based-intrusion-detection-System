@echo off
echo ========================================
echo Pushing to GitHub Repository
echo https://github.com/Silwalkg/AI-powerd-IDS-System
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

REM Check if Git is already initialized
if not exist ".git" (
    echo Step 1: Initializing Git repository...
    git init
    echo.
) else (
    echo Git repository already initialized.
    echo.
)

REM Configure Git (if not already configured)
echo Checking Git configuration...
git config user.name >nul 2>&1
if errorlevel 1 (
    echo Please enter your name:
    set /p username="Name: "
    git config --global user.name "%username%"
)

git config user.email >nul 2>&1
if errorlevel 1 (
    echo Please enter your email:
    set /p useremail="Email: "
    git config --global user.email "%useremail%"
)
echo.

REM Add remote if not exists
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Step 2: Adding remote repository...
    git remote add origin https://github.com/Silwalkg/AI-powerd-IDS-System.git
    echo Remote added successfully.
    echo.
) else (
    echo Remote repository already configured.
    echo Updating remote URL...
    git remote set-url origin https://github.com/Silwalkg/AI-powerd-IDS-System.git
    echo.
)

REM Add all files
echo Step 3: Adding files to Git...
git add .
echo.

REM Check if there are changes to commit
git diff-index --quiet HEAD -- >nul 2>&1
if errorlevel 1 (
    echo Step 4: Creating commit...
    git commit -m "Update: Add comprehensive training guides and documentation"
    echo.
) else (
    echo No changes to commit.
    echo.
)

REM Set main branch
echo Step 5: Setting main branch...
git branch -M main
echo.

REM Push to GitHub
echo Step 6: Pushing to GitHub...
echo This may ask for your GitHub credentials...
echo.
git push -u origin main

if errorlevel 1 (
    echo.
    echo ========================================
    echo Push failed!
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. Authentication failed - You need to provide credentials
    echo 2. Repository doesn't exist or you don't have access
    echo 3. Network connection issue
    echo.
    echo To authenticate:
    echo - Use Personal Access Token instead of password
    echo - Create token at: https://github.com/settings/tokens
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo Success!
    echo ========================================
    echo.
    echo Your code has been pushed to:
    echo https://github.com/Silwalkg/AI-powerd-IDS-System
    echo.
    echo View your repository online!
    echo.
)

pause
