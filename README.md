# 🏘️ Neighborhood Rental Value Analyzer

A comprehensive data analytics tool that helps renters find the best neighborhoods for their budget by analyzing demographics, economic indicators, amenities, and safety data from multiple public APIs.

## 🎯 Features

- **Multi-Source Data Integration**: Combines data from US Census, FRED, OpenStreetMap, and City Open Data APIs
- **Value Scoring System**: Analyzes neighborhoods based on affordability, amenities, transit access, safety, and growth potential
- **Machine Learning Predictions**: Predicts rental demand and prices using ensemble models
- **Interactive Visualizations**: Beautiful charts, maps, and comparisons using Plotly and Folium
- **Personalized Recommendations**: Customizable weights for different factors based on user priorities
- **Cost of Living Analysis**: Compare neighborhoods and identify emerging areas

## 📊 Data Sources

1. **US Census API** - Demographics, income, education, housing characteristics
2. **FRED API** - Economic indicators (unemployment, CPI, housing prices)
3. **OpenStreetMap** - Amenities, distances, transit accessibility
4. **City Open Data** - Crime statistics, school ratings, building permits

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up API keys:**

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
CENSUS_API_KEY=your_census_api_key_here
FRED_API_KEY=your_fred_api_key_here
CITY_DATA_API_KEY=your_city_data_api_key_here  # Optional
```

**Get your API keys:**
- **US Census API**: https://api.census.gov/data/key_signup.html (Free)
- **FRED API**: https://fred.stlouisfed.org/docs/api/api_key.html (Free)
- **City Open Data**: Depends on your city (usually free)

4. **Run the application:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
DATA ANALITCS FINAL PROJECT/
│
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment variables
├── .gitignore                      # Git ignore rules
│
├── data_collectors/                # API integration modules
│   ├── census_collector.py        # US Census API
│   ├── fred_collector.py          # FRED economic data
│   ├── osm_collector.py           # OpenStreetMap data
│   └── city_data_collector.py     # City open data
│
├── analysis/                       # Data processing and analysis
│   ├── data_processor.py          # Data cleaning and feature engineering
│   └── neighborhood_analyzer.py   # Neighborhood scoring and ranking
│
├── models/                         # Machine learning models
│   └── rental_demand_predictor.py # Rental demand prediction
│
└── visualizations/                 # Visualization utilities
    └── visualizer.py              # Charts and maps
```

## 🎮 Usage Guide

### 1. Setting Your Budget

Use the sidebar slider to set your monthly rent budget. The app will filter neighborhoods within your price range.

### 2. Adjusting Priorities

Customize the importance of each factor:
- **Affordability**: How much you value low rent-to-income ratio
- **Amenities**: Restaurants, parks, shopping, etc.
- **Transit Access**: Public transportation availability
- **Safety**: Low crime rates
- **Growth Potential**: Investment and development activity

### 3. Exploring Features

**📊 Overview Tab**
- Market summary statistics
- Affordability scatter plot
- Rent distribution analysis

**🏆 Top Neighborhoods Tab**
- Personalized recommendations based on your budget and priorities
- Value comparison charts
- Detailed neighborhood metrics

**🔍 Detailed Analysis Tab**
- Deep dive into individual neighborhoods
- Spider charts showing characteristic profiles
- Cost comparisons

**📈 Market Trends Tab**
- Cost of living analysis
- Emerging neighborhood identification
- Correlation heatmaps

**🤖 Predictions Tab**
- Machine learning model performance
- Feature importance analysis
- Rent price predictions with confidence intervals

## 🔧 Configuration

### Customizing Analysis Parameters

Edit `config.py` to adjust:

```python
AMENITY_WEIGHTS = {
    'schools': 0.25,
    'transit': 0.20,
    'restaurants': 0.15,
    'parks': 0.15,
    'hospitals': 0.10,
    'shopping': 0.15
}
```

### Cache Settings

Data is cached by default for 7 days. Adjust in `config.py`:
```python
CACHE_EXPIRY_DAYS = 7
```

## 📈 Business Value

This tool provides value to:

1. **Renters**: Make informed decisions about where to live based on comprehensive data
2. **Real Estate Professionals**: Identify high-value areas and market trends
3. **Urban Planners**: Understand neighborhood characteristics and development needs
4. **Investors**: Spot emerging neighborhoods with growth potential

## 🛠️ Technical Details

### Machine Learning Model

- **Algorithm**: Random Forest Regressor (default) or Gradient Boosting
- **Features**: Demographics, income, education, amenities, transit, safety
- **Target**: Median rent prediction
- **Evaluation**: R², RMSE, MAE metrics

### Scoring Methodology

**Value Score** (0-100) = weighted average of:
- Affordability (30%): Based on rent-to-income ratio
- Amenities (20%): Nearby restaurants, parks, shops, schools
- Transit (20%): Public transportation accessibility
- Safety (20%): Crime rate analysis
- Growth (10%): Building permits and economic indicators

## 🐛 Troubleshooting

### API Connection Issues

**Problem**: "Missing API keys" warning

**Solution**: 
1. Ensure `.env` file exists in project root
2. Verify API keys are valid
3. Check internet connection

### ImportError: No module named 'X'

**Problem**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt
```

### Streamlit Port Already in Use

**Problem**: Port 8501 is occupied

**Solution**:
```bash
streamlit run app.py --server.port 8502
```

## 📊 Sample Data Mode

The app includes sample data for demonstration purposes. Enable it in the sidebar to:
- Test functionality without API keys
- Explore features before setting up APIs
- Demonstrate the tool to stakeholders

## 🤝 Contributing

This is an educational project. To extend it:

1. Add more data sources (Zillow, Walk Score, etc.)
2. Implement additional ML models (XGBoost, Neural Networks)
3. Add more visualization types
4. Create neighborhood comparison tools
5. Add historical trend analysis

## 📝 License

This project is for educational purposes. Respect API terms of service and rate limits.

## ⚠️ Disclaimer

This tool provides estimates and insights based on available data. Always:
- Verify information independently
- Visit neighborhoods in person
- Check current market conditions
- Consult with local real estate professionals

## 🙋 Support

For issues or questions:
1. Check API key configuration
2. Verify all dependencies are installed
3. Review error messages in the terminal
4. Check API rate limits

## 🎓 Educational Context

This project demonstrates:
- API integration and data collection
- Data cleaning and feature engineering
- Machine learning model development
- Interactive dashboard creation with Streamlit
- Data visualization best practices
- Geospatial analysis

## 🔮 Future Enhancements

- [ ] Add walkability scores
- [ ] Integrate school rating APIs
- [ ] Include commute time analysis
- [ ] Add historical price trends
- [ ] Implement user accounts for saved searches
- [ ] Create neighborhood comparison reports (PDF)
- [ ] Add mobile-responsive design
- [ ] Include air quality data
- [ ] Add noise level analysis
- [ ] Implement email alerts for new listings

---

**Built with:** Python, Streamlit, Pandas, Scikit-learn, Plotly, Folium

**Version:** 1.0.0

**Last Updated:** December 2025
