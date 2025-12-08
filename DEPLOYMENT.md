# 🚀 GitHub & Streamlit Deployment Guide

## Step 1: Prepare Your Repository

### Files to Upload to GitHub:
✅ **APPRENTFINAL.py** - Main application
✅ **requirements.txt** - Dependencies
✅ **README.md** - Documentation
✅ **config.py** - Configuration
✅ **.gitignore** - Exclude unnecessary files
✅ **QUICKSTART.md** - Quick guide (optional)

### Files NOT to Upload:
❌ `.venv/` folder
❌ `rental_data.db` database
❌ `__pycache__/` folders
❌ `.DS_Store` files

---

## Step 2: Push to GitHub

```bash
# Navigate to your project
cd "/Users/ernestobayon/DATA ANALITCS FINAL PROJECT/APPRENTFINAL"

# Initialize git (if not already done)
git init

# Add all files (respecting .gitignore)
git add .

# Commit your changes
git commit -m "Initial commit - APPRENTFINAL Rental Analyzer"

# Add your GitHub repository as remote
git remote add origin https://github.com/juanbayonugarte-source/REAL-STATE-RENT-ANALYZE-FINAL.git

# Push to GitHub
git push -u origin main
```

---

## Step 3: Deploy to Streamlit Cloud

### Option A: Deploy from GitHub
1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `REAL-STATE-RENT-ANALYZE-FINAL`
5. Set main file path: `APPRENTFINAL.py`
6. Click "Deploy"

### Option B: Deploy from Streamlit Cloud Dashboard
1. Visit https://streamlit.io/cloud
2. Click "New app"
3. Connect your GitHub repository
4. Repository: `juanbayonugarte-source/REAL-STATE-RENT-ANALYZE-FINAL`
5. Branch: `main`
6. Main file: `APPRENTFINAL.py`
7. Click "Deploy!"

---

## Step 4: Verify Deployment

Your app will be available at:
```
https://[your-app-name].streamlit.app
```

Or:
```
https://juanbayonugarte-source-real-state-rent-analyze-final.streamlit.app
```

---

## 📝 Important Notes

### Database Note:
- The SQLite database (`rental_data.db`) will be automatically created when the app runs
- No need to upload it to GitHub
- It will be recreated with sample data on each deployment

### Dependencies:
Make sure your `requirements.txt` includes:
```txt
streamlit
pandas
numpy
plotly
```

### Python Version:
Streamlit Cloud uses Python 3.9+ by default. Your code is compatible.

---

## 🔧 Troubleshooting

### Issue: App won't start
**Solution:** Check that `APPRENTFINAL.py` is in the root directory

### Issue: Missing dependencies
**Solution:** Verify `requirements.txt` has all packages without version conflicts

### Issue: Database errors
**Solution:** The database is auto-created, ensure SQLite code runs on startup

### Issue: Port errors
**Solution:** Streamlit Cloud handles ports automatically - no config needed

---

## 📊 What Happens on Deployment

1. Streamlit Cloud clones your GitHub repository
2. Installs dependencies from `requirements.txt`
3. Runs `APPRENTFINAL.py`
4. Creates `rental_data.db` automatically
5. Makes your app publicly accessible

---

## 🎯 Quick Command Reference

```bash
# Check git status
git status

# Add all files
git add .

# Commit changes
git commit -m "Your message here"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

---

## ✅ Pre-Deployment Checklist

- [ ] All required files in repository
- [ ] `.gitignore` excludes `.venv/` and `.db` files
- [ ] `requirements.txt` is complete and correct
- [ ] No hardcoded secrets or API keys
- [ ] `APPRENTFINAL.py` runs without errors locally
- [ ] README.md is informative
- [ ] Repository is public (or you have Streamlit Cloud Pro)

---

## 🌐 After Deployment

Your app will be live and accessible to anyone with the URL!

**Features that work on Streamlit Cloud:**
✅ All 3 tabs (Welcome, Neighborhoods, SQL)
✅ SQLite database with queries
✅ Interactive filters and charts
✅ Real-time data updates
✅ Color-coded recommendations

---

Good luck with your deployment! 🚀
