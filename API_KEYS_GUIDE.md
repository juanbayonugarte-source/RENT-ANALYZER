# Getting API Keys for Enhanced Features

To use real-time data from Zillow and Walk Score, you'll need to sign up for API keys:

## 🏠 Realty Mole API

**What it provides:** Real rental price estimates, property valuations, market data

**How to get it:**

1. Go to [Realty Mole](https://realtymole.com/api)
2. Click "Get API Key"
3. Fill out the form with your email
4. Check your email for the API key
   - Free tier: 100 requests/month
5. Add to Streamlit secrets:
   ```toml
   REALTYMOLE_API_KEY = "your-realtymole-api-key-here"
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
REALTYMOLE_API_KEY = "9772b19d1b0a425cbfef239bb982f00e"
WALKSCORE_API_KEY = "your-walkscore-api-key-here"
```

## 🔧 Local Development (.env file)

For local testing, create a `.env` file in your project root:

```env
CENSUS_API_KEY=d89f2308a0eef3819958d4afe09eb6673a96121e
FRED_API_KEY=eb9f52a46863eceb6c89aaffb5fedc3c
REALTYMOLE_API_KEY=9772b19d1b0a425cbfef239bb982f00e
WALKSCORE_API_KEY=your-walkscore-api-key-here
```

## ✨ Benefits of Real Data

### With Realty Mole API:
- ✅ Professional rental price estimates
- ✅ Property valuations and price ranges
- ✅ Property details (bedrooms, bathrooms, sqft)
- ✅ More accurate affordability calculations
- ✅ 100 free requests/month

### With Walk Score API:
- ✅ Professional walkability scores (0-100)
- ✅ Real transit accessibility data
- ✅ Bike-friendliness scores
- ✅ Detailed neighborhood descriptions

## 🎯 Without API Keys

The app still works great with sample data! All features function normally, but with simulated data instead of real-time information.
