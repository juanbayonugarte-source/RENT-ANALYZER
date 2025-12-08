#!/bin/bash

# APPRENTFINAL Launch Script
# Easy way to launch the Neighborhood Rental Value Analyzer

echo "=================================="
echo "  APPRENTFINAL"
echo "  Neighborhood Rental Analyzer"
echo "=================================="
echo ""
echo "Starting Streamlit application..."
echo ""

# Navigate to project directory
cd "/Users/ernestobayon/DATA ANALITCS FINAL PROJECT/APPRENTFINAL"

# Activate virtual environment and run
source .venv/bin/activate
streamlit run APPRENTFINAL.py

echo ""
echo "Application stopped."
