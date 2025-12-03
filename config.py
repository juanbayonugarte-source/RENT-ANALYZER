"""Configuration management for the Rental Value Analyzer."""
import os

# Try to load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not available, skip it (will use env vars or Streamlit secrets)
    pass

def _get_secret(key, default=None):
    """Get secret from Streamlit secrets or environment variables."""
    try:
        import streamlit as st
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (ImportError, FileNotFoundError, KeyError):
        pass
    # Fall back to environment variables (for local development)
    return os.getenv(key, default)

class Config:
    """Application configuration."""
    
    # API Keys - dynamically loaded from secrets or env vars
    CENSUS_API_KEY = _get_secret('CENSUS_API_KEY')
    FRED_API_KEY = _get_secret('FRED_API_KEY')
    CITY_DATA_API_KEY = _get_secret('CITY_DATA_API_KEY')
    REALTYMOLE_API_KEY = _get_secret('REALTYMOLE_API_KEY', '9772b19d1b0a425cbfef239bb982f00e')  # For rental data
    WALKSCORE_API_KEY = _get_secret('WALKSCORE_API_KEY')  # For Walk Score
    
    # Default settings
    DEFAULT_STATE = os.getenv('DEFAULT_STATE', 'CA')
    DEFAULT_CITY = os.getenv('DEFAULT_CITY', 'Los Angeles')
    
    # California city coordinates for mapping
    CITY_CENTERS = {
        'Los Angeles': (34.0522, -118.2437),
        'San Francisco': (37.7749, -122.4194),
        'San Diego': (32.7157, -117.1611),
        'San Jose': (37.3382, -121.8863),
        'Oakland': (37.8044, -122.2712),
    }
    
    # Census API endpoints
    CENSUS_BASE_URL = "https://api.census.gov/data"
    CENSUS_YEAR = 2021
    
    # FRED API settings
    FRED_BASE_URL = "https://api.stlouisfed.org/fred"
    
    # OpenStreetMap settings
    OSM_NOMINATIM_URL = "https://nominatim.openstreetmap.org"
    OSM_USER_AGENT = "rental-value-analyzer"
    
    # Cache settings
    CACHE_DIR = "data/cache"
    CACHE_EXPIRY_DAYS = 7
    
    # Analysis parameters
    AMENITY_WEIGHTS = {
        'schools': 0.25,
        'transit': 0.20,
        'restaurants': 0.15,
        'parks': 0.15,
        'hospitals': 0.10,
        'shopping': 0.15
    }
    
    # Visualization settings
    MAP_DEFAULT_ZOOM = 12
    COLOR_SCHEME = 'Viridis'
    
    @classmethod
    def validate(cls):
        """Validate that required API keys are present."""
        missing_keys = []
        if not cls.CENSUS_API_KEY:
            missing_keys.append('CENSUS_API_KEY')
        if not cls.FRED_API_KEY:
            missing_keys.append('FRED_API_KEY')
        
        if missing_keys:
            return False, missing_keys
        return True, []
