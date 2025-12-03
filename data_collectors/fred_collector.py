"""FRED API data collector for economic indicators."""
import requests
import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
from config import Config

class FREDDataCollector:
    """Collect economic indicators from FRED API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the FRED data collector."""
        self.api_key = api_key or Config.FRED_API_KEY
        self.base_url = "https://api.stlouisfed.org/fred"
        
    def get_series(self, series_id: str, start_date: Optional[str] = None) -> pd.DataFrame:
        """
        Get time series data from FRED.
        
        Args:
            series_id: FRED series ID
            start_date: Start date in YYYY-MM-DD format
            
        Returns:
            DataFrame with time series data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': start_date
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df[['date', 'value']].dropna()
            df.columns = ['date', series_id]
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching FRED data for {series_id}: {e}")
            return pd.DataFrame()
    
    def get_economic_indicators(self, state_code: Optional[str] = None) -> pd.DataFrame:
        """
        Get key economic indicators.
        
        Args:
            state_code: Two-letter state code (e.g., 'CA' for California)
            
        Returns:
            DataFrame with economic indicators
        """
        # National indicators
        national_series = {
            'UNRATE': 'unemployment_rate',
            'CPIAUCSL': 'cpi',
            'MORTGAGE30US': 'mortgage_rate_30yr',
            'CSUSHPISA': 'case_shiller_index',
            'MSPUS': 'median_home_price',
            'RHORUSQ156N': 'homeownership_rate',
        }
        
        dfs = []
        for series_id, name in national_series.items():
            df = self.get_series(series_id)
            if not df.empty:
                df = df.rename(columns={series_id: name})
                dfs.append(df)
        
        # Merge all series
        if dfs:
            result = dfs[0]
            for df in dfs[1:]:
                result = result.merge(df, on='date', how='outer')
            result = result.sort_values('date')
            return result
        
        return pd.DataFrame()
    
    def get_state_indicators(self, state_code: str) -> pd.DataFrame:
        """
        Get state-level economic indicators.
        
        Args:
            state_code: Two-letter state code
            
        Returns:
            DataFrame with state indicators
        """
        # State unemployment rate series ID format: STATEABBUR (e.g., CAUR for California)
        state_series = {
            f'{state_code}UR': 'state_unemployment_rate',
            f'{state_code}POP': 'state_population',
        }
        
        dfs = []
        for series_id, name in state_series.items():
            df = self.get_series(series_id)
            if not df.empty:
                df = df.rename(columns={series_id: name})
                dfs.append(df)
        
        if dfs:
            result = dfs[0]
            for df in dfs[1:]:
                result = result.merge(df, on='date', how='outer')
            result = result.sort_values('date')
            return result
        
        return pd.DataFrame()
    
    def get_latest_indicators(self) -> dict:
        """Get the most recent values for key indicators."""
        indicators = self.get_economic_indicators()
        
        if indicators.empty:
            return {}
        
        latest = indicators.iloc[-1].to_dict()
        latest.pop('date', None)
        
        return latest
