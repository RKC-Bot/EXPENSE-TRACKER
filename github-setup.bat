@echo off
REM GitHub Deployment Script for Expense Tracker
REM Run this file: github-setup.bat

setlocal enabledelayedexpansion

set GITHUB_USERNAME=rkc-bot
set REPO_NAME=expense-tracker
set PROJECT_PATH=C:\Users\DELL\OneDrive\RICHA\COURSES\AI PROJECTS\CAPSTONE PROJECT\New folder\expense_tracker\expense_tracker

echo.
echo ========================================
echo GitHub Deployment Setup
echo ========================================
echo.

cd /d "%PROJECT_PATH%"
echo Working directory: %cd%
echo.

echo [1/6] Initializing Git repository...
git init
if errorlevel 1 (
    echo X Failed to initialize git
    exit /b 1
)
echo OK Git initialized
echo.

echo [2/6] Configuring Git user...
git config user.email "noreply@github.com"
git config user.name "Expense Tracker Bot"
echo OK Git configured
echo.

echo [3/6] Adding files to staging area...
git add .
echo OK Files staged
echo.

echo [4/6] Creating initial commit...
git commit -m "Initial: AI Expense Tracker with OCR and Voice Entry"
if errorlevel 1 (
    echo X Failed to create commit
    exit /b 1
)
echo OK Commit created
echo.

echo [5/6] Setting branch to main...
git branch -M main
echo OK Branch set to main
echo.

echo [6/6] Adding GitHub remote...
set REMOTE_URL=https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
git remote add origin %REMOTE_URL%
echo OK Remote added: %REMOTE_URL%
echo.

echo ========================================
echo NEXT STEP: Push to GitHub
echo ========================================
echo.
echo Run this command to push your code:
echo.
echo git push -u origin main
echo.
echo When prompted for credentials:
echo   Username: %GITHUB_USERNAME%
echo   Password: [Your Personal Access Token]
echo.
echo Create token: https://github.com/settings/tokens
echo.
echo ========================================
echo.

git status
pause
