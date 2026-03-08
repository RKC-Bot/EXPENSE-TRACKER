# ✅ Pre-Deployment Checklist for Streamlit Cloud

## Repository Setup
- [ ] Created public GitHub repository
- [ ] All source code is in the repo
- [ ] `.gitignore` excludes `.venv/`, `__pycache__/`, and `*.db`
- [ ] `requirements.txt` is in the project root
- [ ] `main.py` is in the project root
- [ ] Pushed all commits to GitHub (`git push`)

## Code Quality
- [ ] All modules can be imported without errors
- [ ] No hardcoded credentials/passwords in code
- [ ] No absolute file paths (use relative paths)
- [ ] Database is created on-the-fly (not required in repo)
- [ ] All dependencies are listed in `requirements.txt`

## Streamlit Specifics
- [ ] Using `@st.cache_resource` for expensive operations
- [ ] No blocking I/O at module level (lazy loading)
- [ ] All secrets stored in Streamlit Cloud secrets, not in code
- [ ] Using Python 3.9+ compatible code
- [ ] No matplotlib backend issues (use Plotly instead)

## Files to Include
- ✓ `main.py` - Main Streamlit app
- ✓ `requirements.txt` - Dependencies
- ✓ `packages.txt` - System packages (Tesseract)
- ✓ `modules/` - All Python modules
- ✓ `README.md` - Documentation
- ✓ `.streamlit/config.toml` - App configuration
- ✓ `.gitignore` - Exclude unnecessary files

## Files to Exclude
- ✗ `.venv/` or `venv/`
- ✗ `__pycache__/`
- ✗ `*.pyc` files
- ✗ `db/expenses.db` (generated at runtime)
- ✗ `.env` files with secrets
- ✗ Large data files (>200MB)

## Deployment Steps
1. [ ] Navigate to https://share.streamlit.io/
2. [ ] Log in with GitHub account
3. [ ] Click "New app"
4. [ ] Select your repository
5. [ ] Select `main` branch
6. [ ] Set main file: `main.py`
7. [ ] Click "Deploy"
8. [ ] Wait ~2-3 minutes for deployment
9. [ ] Share the public URL with your team

## Post-Deployment
- [ ] Test the app at the provided URL
- [ ] Try all major features (upload, voice, OCR)
- [ ] Check console logs for errors
- [ ] Configure secrets if needed
- [ ] Share feedback link with team
- [ ] Monitor app performance

---

## Estimated Build Time
- **First deployment:** 3-5 minutes (installs all dependencies)
- **Subsequent updates:** 1-2 minutes (caches dependencies)
- **Cold start:** ~3 seconds (first request after idle)

## Common Issues & Fixes

### Issue: "Module not found" error
**Fix:** Ensure all imports use relative paths: `from modules.database import ...`

### Issue: Database is empty on reload
**Fix:** This is expected. Use persistent cloud database for production.

### Issue: Slow initial load
**Fix:** EasyOCR downloads models on first inference (~5 min). Subsequent calls are instant.

### Issue: App times out during build
**Fix:** Use `streamlit_requirements.txt` instead (smaller torch/torchvision versions)

---

## Support Links
- **Streamlit Docs:** https://docs.streamlit.io/
- **Streamlit Community Cloud:** https://share.streamlit.io/
- **GitHub Help:** https://docs.github.com/
- **Python Packaging:** https://packaging.python.org/

**Your app is ready for production! 🚀**
