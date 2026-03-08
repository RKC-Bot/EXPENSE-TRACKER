# 🚀 Deployment Guide - Streamlit Community Cloud

## Prerequisites
- GitHub Account (free at https://github.com/signup)
- Streamlit Account (free at https://streamlit.io/cloud)

---

## Step 1: Create GitHub Repository

1. Go to **https://github.com/new**
2. Fill in:
   - **Repository name:** `expense-tracker` (or your preferred name)
   - **Description:** "AI-powered Expense & Petty Cash Tracker with OCR and Voice Entry"
   - **Public** (for free Streamlit Cloud deployment)
   - ✓ "Initialize with README" (optional)
3. Click **"Create repository"**

---

## Step 2: Initialize Git Locally & Push Code

Open PowerShell in your project folder and run:

```powershell
# Navigate to project folder
cd "C:\Users\DELL\OneDrive\RICHA\COURSES\AI PROJECTS\CAPSTONE PROJECT\New folder\expense_tracker\expense_tracker"

# Initialize Git
git init
git add .
git commit -m "Initial commit: AI Expense Tracker with OCR and Voice Entry"

# Add remote (replace YOUR_USERNAME and YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub (will ask for credentials)
git branch -M main
git push -u origin main
```

**Note:** You'll be prompted for GitHub credentials. Use:
- **Username:** Your GitHub username
- **Password:** Your GitHub Personal Access Token (create at https://github.com/settings/tokens)

---

## Step 3: Deploy to Streamlit Cloud

1. Go to **https://share.streamlit.io/**
2. Click **"New app"**
3. Fill in:
   - **GitHub:** Link your GitHub account (first time only)
   - **Repository:** `YOUR_USERNAME/expense-tracker`
   - **Branch:** `main`
   - **Main file path:** `main.py`
4. Click **"Deploy"**

The app will deploy automatically! 🎉

---

## Step 4: Share Your App

Once deployed, your app will be available at:
```
https://YOUR_USERNAME-expense-tracker.streamlit.app
```

Share this link with colleagues, team members, or clients!

---

## ⚠️ Important Notes for Streamlit Cloud

### 1. Python Version
Streamlit Cloud uses **Python 3.11** by default (compatible!). Your code works perfectly.

### 2. Tesseract OCR
Streamlit Cloud includes Tesseract OCR pre-installed. No additional setup needed.

### 3. Database Persistence
- Each app deployment gets a temporary file system
- Database is reset on every app restart
- For **persistent storage**, consider:
  - **Option A:** Cloud SQL (GCP, AWS, AWS RDS)
  - **Option B:** Streamlit Cloud's `@st.cache_resource` + cloud backup
  - **Option C:** Create account system with cloud database

### 4. Secrets Management
For sensitive data (passwords, API keys):
1. Go to app settings → **Secrets**
2. Add in format:
   ```toml
   db_password = "your_password"
   api_key = "your_key"
   ```
3. Access in code: `st.secrets["db_password"]`

### 5. Upload Size Limit
Maximum upload file size: **200MB** (includes invoices)

---

## Step 5: Enable Advanced Features (Optional)

### A. Custom Domain
- Go to Streamlit Cloud dashboard
- App settings → Custom domain
- Add your own domain (e.g., `expense-tracker.yourcompany.com`)

### B. Access Control
For private access (team only):
- Streamlit Cloud → App access settings
- White-list specific GitHub users
- Or use: Streamlit Cloud Viewer Passkey (beta)

### C. Scheduled Jobs
To run tasks automatically (e.g., daily backup):
- Use GitHub Actions + Cloud Functions
- Or embed in Streamlit using `schedule` library

---

## Troubleshooting

### App Deploy Fails
- Check **console logs** in Streamlit Cloud
- Verify all dependencies are in `requirements.txt`
- Ensure `main.py` exists in repo root

### Slow Initial Load
- EasyOCR downloads models on first run (~300MB)
- Subsequent loads are cached
- Consider pre-caching in startup

### Database Resets
- Use persistent cloud database instead
- Or save state to GitHub via API

---

## Cost

- **Streamlit Community Cloud:** FREE ✓
- **Custom domain:** $10-15/month (optional)
- **Cloud database:** Pay-as-you-go ($0-50/month depending on usage)

---

## Next Steps

After deployment, you can:
1. ✅ Share link with team for immediate testing
2. ✅ Gather feedback and iterate quickly
3. ✅ Monitor usage with Streamlit analytics
4. ✅ Move to production (serverless or Docker)
5. ✅ Integrate with CI/CD pipeline

**Your app is production-ready! 🎉**
