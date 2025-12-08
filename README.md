# APPRENTFINAL - Neighborhood Rental Value Analyzer

## 🏘️ California Rental Market Analysis Tool

A comprehensive Streamlit application for analyzing neighborhood rental values across California using SQLite database and interactive visualizations.

---

## 📋 Features

- **🏠 Welcome Overview**: California-wide market statistics and county comparisons
- **📊 Top Neighborhoods**: Personalized recommendations with color-coded ratings
- **💾 SQL Database Analysis**: Live database queries and statistics
- **🔍 Advanced Filters**: County, budget, bedrooms, and custom priority weights
- **📈 Interactive Charts**: Plotly visualizations with drill-down capabilities
- **🗄️ SQLite Database**: Structured data storage with efficient SQL queries

---

## 🚀 Quick Start

### Launch the Application

```bash
cd "/Users/ernestobayon/DATA ANALITCS FINAL PROJECT/APPRENTFINAL"
streamlit run APPRENTFINAL.py
```

The app will automatically open in your browser at `http://localhost:8501`

---

## 📦 Requirements

All dependencies are installed in the virtual environment (`.venv`):
- streamlit
- pandas
- numpy
- plotly
- sqlite3 (built-in)

---

## 🎯 How to Use

### 1. **Sidebar Filters**
   - Select a county (or view all California)
   - Set your monthly rent budget
   - Choose number of bedrooms
   - Adjust priority weights (Affordability, Amenities, Transit, Safety, Schools, Growth)

### 2. **Welcome Overview Tab**
   - View California-wide statistics
   - See top 10 counties by value score
   - Preview neighborhoods in selected county

### 3. **Top Neighborhoods Tab**
   - Browse color-coded recommendations
   - View detailed metrics and scores
   - Export filtered results

### 4. **SQL Database Analysis Tab**
   - View active SQL queries
   - Explore database statistics
   - See sample records

---

## 🗂️ Project Structure

```
APPRENTFINAL/
├── APPRENTFINAL.py          # Main Streamlit application
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── config.py               # Configuration settings
├── rental_data.db          # SQLite database (auto-generated)
└── .venv/                  # Virtual environment
```

---

## 💾 Database Schema

The SQLite database (`rental_data.db`) contains a `neighborhoods` table with:
- Location data (name, county, latitude, longitude)
- Demographics (population, income, age, education)
- Rental metrics (median rent, affordability score)
- Quality scores (amenities, transit, safety, schools, growth)
- Calculated metrics (value_score, rank)

---

## ✨ Enjoy exploring California's rental market!
