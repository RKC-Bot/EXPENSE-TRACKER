#!/usr/bin/env pwsh
# GitHub Deployment Script for Expense Tracker

# Set your GitHub credentials
$GITHUB_USERNAME = "rkc-bot"
$REPO_NAME = "expense-tracker"
$PROJECT_PATH = "C:\Users\DELL\OneDrive\RICHA\COURSES\AI PROJECTS\CAPSTONE PROJECT\New folder\expense_tracker\expense_tracker"

# Navigate to project
Set-Location -Path $PROJECT_PATH
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Green

# Initialize Git repository
Write-Host "`n[1/6] Initializing Git repository..." -ForegroundColor Cyan
git init
if ($?) { Write-Host "✓ Git initialized" -ForegroundColor Green } else { Write-Host "✗ Failed to init git" -ForegroundColor Red; exit 1 }

# Configure Git user (optional but recommended)
Write-Host "`n[2/6] Configuring Git user..." -ForegroundColor Cyan
git config user.email "noreply@github.com"
git config user.name "GitHub User"
Write-Host "✓ Git user configured" -ForegroundColor Green

# Add all files
Write-Host "`n[3/6] Adding files to staging area..." -ForegroundColor Cyan
git add .
Write-Host "✓ Files staged" -ForegroundColor Green

# Create initial commit
Write-Host "`n[4/6] Creating initial commit..." -ForegroundColor Cyan
git commit -m "Initial commit: AI Expense Tracker with OCR and Voice Entry"
if ($?) { Write-Host "✓ Commit created" -ForegroundColor Green } else { Write-Host "✗ Failed to commit" -ForegroundColor Red; exit 1 }

# Rename branch to main
Write-Host "`n[5/6] Setting branch to main..." -ForegroundColor Cyan
git branch -M main
Write-Host "✓ Branch set to main" -ForegroundColor Green

# Add remote origin
Write-Host "`n[6/6] Adding GitHub remote..." -ForegroundColor Cyan
$REMOTE_URL = "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
git remote add origin $REMOTE_URL
Write-Host "✓ Remote added: $REMOTE_URL" -ForegroundColor Green

# Show git status
Write-Host "`n" -ForegroundColor Cyan
git status

Write-Host "`n" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "NEXT STEP: Push to GitHub" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════"
Write-Host ""
Write-Host "Run this command to push your code to GitHub:" -ForegroundColor Cyan
Write-Host ""
Write-Host "git push -u origin main" -ForegroundColor Green
Write-Host ""
Write-Host "When prompted for credentials:" -ForegroundColor Yellow
Write-Host "  Username: $GITHUB_USERNAME" -ForegroundColor White
Write-Host "  Password: [Your GitHub Personal Access Token]" -ForegroundColor White
Write-Host ""
Write-Host "Create a token at: https://github.com/settings/tokens" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════`n"
