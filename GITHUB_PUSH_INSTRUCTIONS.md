# 📌 GitHub & Streamlit Cloud Deployment Guide

## Quick Setup (Automated Scripts Provided)

I've created **two automated scripts** to make this easier:

### Option A: PowerShell Script (Recommended for Windows)
```powershell
powershell -ExecutionPolicy Bypass -File ".\github-setup.ps1"
```

### Option B: Batch Script
```batch
github-setup.bat
```

### Option C: Manual Commands (Step by Step)

If the scripts don't work, run these commands manually in PowerShell:

```powershell
# 1. Navigate to your project
cd "C:\Users\DELL\OneDrive\RICHA\COURSES\AI PROJECTS\CAPSTONE PROJECT\New folder\expense_tracker\expense_tracker"

# 2. Initialize Git
git init

# 3. Configure Git user (one-time setup)
git config user.email "your-email@example.com"
git config user.name "Your Name"

# 4. Add all files
git add .

# 5. Create initial commit
git commit -m "Initial: AI Expense Tracker with OCR and Voice Entry"

# 6. Rename branch to main
git branch -M main

# 7. Add GitHub remote
git remote add origin https://github.com/rkc-bot/expense-tracker.git

# 8. Push to GitHub
git push -u origin main
```

---

## What Happens in Each Step

| Step | Command | What It Does |
|------|---------|------------|
| 1 | `git init` | Creates `.git` folder to track changes |
| 2 | `git config` | Sets your name/email for commits |
| 3 | `git add .` | Stages all files for commit |
| 4 | `git commit` | Creates a snapshot of your code |
| 5 | `git branch -M main` | Renames default branch to `main` |
| 6 | `git remote add` | Links to your GitHub repository |
| 7 | `git push -u origin main` | Uploads code to GitHub |

---

## Before You Run: Create GitHub Repository

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name:** `expense-tracker`
   - **Description:** "AI-powered Expense & Petty Cash Tracker with OCR and Voice Entry"
   - **Public** (required for free Streamlit Cloud)
3. Click **"Create repository"**
4. ✅ Repository is now ready for code!

---

## GitHub Authentication

When you run `git push`, Git will ask for credentials:

### Option 1: Personal Access Token (Recommended)
1. Go to **https://github.com/settings/tokens**
2. Click **"Generate new token"**
3. Select scope: **`repo`** (full control of repositories)
4. Click **"Generate token"**
5. Copy the token (you won't see it again!)
6. When Git prompts for password, paste the token

### Option 2: Built-in GitHub CLI (Alternative)
```powershell
# Install GitHub CLI (if not already installed)
winget install GitHub.cli

# Authenticate
gh auth login

# Then use git commands normally
git push -u origin main
```

---

## ✅ Verify Your Push

After running `git push -u origin main`, you should see:
```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Delta compression using up to 8 threads
Compressing objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), done.
Total XX (delta XX), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (XX/XX), done.

To https://github.com/rkc-bot/expense-tracker.git
 * [new branch]      main -> main
Branch 'main' set to track remote branch 'main' from 'origin'.
```

✅ **Check:** Visit https://github.com/rkc-bot/expense-tracker and confirm your code is there!

---

## Next: Deploy to Streamlit Cloud

Once your code is on GitHub:

1. Go to **https://share.streamlit.io/**
2. Click **"New app"**
3. Authorize with GitHub (first time only)
4. Select:
   - **Repository:** `rkc-bot/expense-tracker`
   - **Branch:** `main`
   - **Main file:** `main.py`
5. Click **"Deploy"**
6. ✅ Wait 2-3 minutes...
7. 🎉 Your app is live at `https://rkc-bot-expense-tracker.streamlit.app`

---

## Common Issues & Fixes

### ❌ "fatal: not a git repository"
**Fix:** Run `git init` first

### ❌ "nothing to commit"
**Fix:** Make sure you have `git add .` before `git commit`

### ❌ "remote origin already exists"
**Fix:** Remove the old remote: `git remote remove origin`

### ❌ "fatal: Authentication failed"
**Fix:** Use Personal Access Token instead of password

### ❌ "Repository not found"
**Fix:** Create the repository on GitHub first at https://github.com/new

---

## Files Already Prepared for Deployment

✅ `.gitignore` - Excludes database, venv, cache  
✅ `requirements.txt` - Python dependencies  
✅ `packages.txt` - System packages (Tesseract)  
✅ `main.py` - Streamlit app  
✅ `modules/` - All Python modules  
✅ `README.md` - Documentation  

**Everything is ready! Just push it now.** 🚀
