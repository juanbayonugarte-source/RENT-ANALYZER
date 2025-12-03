"""Data processing and analysis utilities."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from config import Config

class DataProcessor:
    """Process and clean collected data."""
    
    @staticmethod
    def clean_census_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize Census data.
        
        Args:
            df: Raw Census DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        # Remove rows with missing critical data
        critical_cols = ['total_population', 'median_income', 'median_rent']
        df = df.dropna(subset=[col for col in critical_cols if col in df.columns])
        
        # Handle outliers
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['state', 'county', 'tract']:
                # Remove extreme outliers (beyond 3 standard deviations)
                mean = df[col].mean()
                std = df[col].std()
                df = df[df[col].between(mean - 3*std, mean + 3*std)]
        
        return df
    
    @staticmethod
    def calculate_affordability_index(
        median_rent: float, 
        median_income: float
    ) -> float:
        """
        Calculate affordability index (0-100, higher is more affordable).
        
        The rule of thumb is rent should be <= 30% of income.
        
        Args:
            median_rent: Monthly median rent
            median_income: Annual median income
            
        Returns:
            Affordability score
        """
        if median_income == 0 or pd.isna(median_income):
            return 0.0
        
        monthly_income = median_income / 12
        rent_to_income_ratio = median_rent / monthly_income
        
        # Score: 100 if ratio <= 0.25, 0 if ratio >= 0.50
        if rent_to_income_ratio <= 0.25:
            score = 100
        elif rent_to_income_ratio >= 0.50:
            score = 0
        else:
            # Linear scale between 25-50% range
            score = 100 - ((rent_to_income_ratio - 0.25) / 0.25) * 100
        
        return max(0, min(100, score))
    
    @staticmethod
    def calculate_amenity_score(amenities: Dict[str, int]) -> float:
        """
        Calculate composite amenity score (0-100).
        
        Args:
            amenities: Dictionary of amenity counts
            
        Returns:
            Amenity score
        """
        weights = Config.AMENITY_WEIGHTS
        
        # Normalize counts (using log scale to handle varying ranges)
        normalized_scores = {}
        for amenity, count in amenities.items():
            if amenity in weights:
                # Score based on log of count + 1
                normalized = min(100, np.log1p(count) * 20)
                normalized_scores[amenity] = normalized
        
        # Weighted average
        total_score = sum(
            normalized_scores.get(amenity, 0) * weight 
            for amenity, weight in weights.items()
        )
        
        return round(total_score, 2)
    
    @staticmethod
    def calculate_growth_potential(
        permits_df: pd.DataFrame,
        economic_indicators: Dict[str, float]
    ) -> float:
        """
        Calculate neighborhood growth potential score (0-100).
        
        Args:
            permits_df: Building permits DataFrame
            economic_indicators: Economic indicator values
            
        Returns:
            Growth potential score
        """
        score = 50.0  # Base score
        
        # Building activity boost
        if not permits_df.empty:
            recent_permits = len(permits_df)
            permit_score = min(30, recent_permits * 0.5)
            score += permit_score
        
        # Economic indicators boost
        if 'unemployment_rate' in economic_indicators:
            unemployment = economic_indicators['unemployment_rate']
            # Lower unemployment = higher score
            if unemployment < 4:
                score += 20
            elif unemployment < 6:
                score += 10
        
        return min(100, score)
    
    @staticmethod
    def calculate_safety_score(crime_data: pd.DataFrame) -> float:
        """
        Calculate safety score (0-100, higher is safer).
        
        Args:
            crime_data: DataFrame with crime incidents
            
        Returns:
            Safety score
        """
        if crime_data.empty:
            return 75.0  # Neutral score when no data
        
        # Count crimes by severity if available
        crime_count = len(crime_data)
        
        # Base score on frequency (assuming per year within 1km radius)
        if crime_count <= 10:
            score = 95
        elif crime_count <= 25:
            score = 85
        elif crime_count <= 50:
            score = 70
        elif crime_count <= 100:
            score = 55
        else:
            score = 40
        
        # Adjust for severity if available
        if 'severity' in crime_data.columns:
            high_severity = (crime_data['severity'] == 'High').sum()
            score -= high_severity * 2
        
        return max(0, min(100, score))
    
    @staticmethod
    def normalize_scores(*scores: float) -> List[float]:
        """
        Normalize multiple scores to 0-100 range.
        
        Args:
            *scores: Variable number of scores
            
        Returns:
            List of normalized scores
        """
        scores_array = np.array(scores)
        min_score = scores_array.min()
        max_score = scores_array.max()
        
        if max_score == min_score:
            return [50.0] * len(scores)
        
        normalized = (scores_array - min_score) / (max_score - min_score) * 100
        return normalized.tolist()
    
    @staticmethod
    def create_feature_matrix(
        census_df: pd.DataFrame,
        amenity_scores: List[float],
        transit_scores: List[float],
        safety_scores: List[float]
    ) -> pd.DataFrame:
        """
        Create feature matrix for machine learning.
        
        Args:
            census_df: Census demographics
            amenity_scores: Amenity scores
            transit_scores: Transit accessibility scores
            safety_scores: Safety scores
            
        Returns:
            Feature matrix DataFrame
        """
        features = census_df.copy()
        
        # Add derived scores
        features['amenity_score'] = amenity_scores
        features['transit_score'] = transit_scores
        features['safety_score'] = safety_scores
        
        # Add interaction features
        if 'median_income' in features.columns and 'median_rent' in features.columns:
            features['affordability'] = features.apply(
                lambda row: DataProcessor.calculate_affordability_index(
                    row['median_rent'], row['median_income']
                ), axis=1
            )
        
        return features
