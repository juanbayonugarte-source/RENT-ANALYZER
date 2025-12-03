# Getting API Keys for Enhanced Features

To use real-time data from Zillow and Walk Score, you'll need to sign up for API keys:

## 🏠 Zillow Data (via RapidAPI)

**What it provides:** Real rental prices, property listings, market trends

**How to get it:**

1. Go to [RapidAPI](https://rapidapi.com/)
2. Create a free account
3. Subscribe to [Zillow API](https://rapidapi.com/apimaker/api/zillow-com1)
   - Free tier: 500 requests/month
4. Copy your **X-RapidAPI-Key**
5. Add to Streamlit secrets:
   ```toml
   RAPIDAPI_KEY = "your-rapidapi-key-here"
   ```

## 🚶 Walk Score API

**What it provides:** Walk Score, Transit Score, Bike Score for accurate walkability data

**How to get it:**

1. Go to [Walk Score Professional](https://www.walkscore.com/professional/api.php)
2. Fill out the API request form
3. Wait for approval (usually 1-2 business days)
4. Copy your **API key**
5. Add to Streamlit secrets:
   ```toml
   WALKSCORE_API_KEY = "your-walkscore-api-key-here"
   ```

## 📋 Complete Streamlit Secrets Setup

In your Streamlit Cloud app settings, add all keys:

```toml
# Existing keys
CENSUS_API_KEY = "d89f2308a0eef3819958d4afe09eb6673a96121e"
FRED_API_KEY = "eb9f52a46863eceb6c89aaffb5fedc3c"

# New keys (add these)
RAPIDAPI_KEY = "your-rapidapi-key-here"
WALKSCORE_API_KEY = "your-walkscore-api-key-here"
```

## 🔧 Local Development (.env file)

For local testing, create a `.env` file in your project root:

```env
CENSUS_API_KEY=d89f2308a0eef3819958d4afe09eb6673a96121e
FRED_API_KEY=eb9f52a46863eceb6c89aaffb5fedc3c
RAPIDAPI_KEY=your-rapidapi-key-here
WALKSCORE_API_KEY=your-walkscore-api-key-here
```

## ✨ Benefits of Real Data

### With Zillow API:
- ✅ Real rental prices from actual listings
- ✅ Property details (bedrooms, bathrooms, sqft)
- ✅ Market trends and inventory data
- ✅ More accurate affordability calculations

### With Walk Score API:
- ✅ Professional walkability scores (0-100)
- ✅ Real transit accessibility data
- ✅ Bike-friendliness scores
- ✅ Detailed neighborhood descriptions

## 🎯 Without API Keys

The app still works great with sample data! All features function normally, but with simulated data instead of real-time information.
