"""Neighborhood value analyzer."""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from analysis.data_processor import DataProcessor

class NeighborhoodAnalyzer:
    """Analyze and rank neighborhoods based on multiple factors."""
    
    def __init__(self):
        """Initialize the neighborhood analyzer."""
        self.processor = DataProcessor()
        
    def calculate_value_score(
        self,
        affordability: float,
        amenities: float,
        transit: float,
        safety: float,
        growth: float = 50.0,
        ocean: float = 50.0,
        weights: Dict[str, float] = None
    ) -> float:
        """
        Calculate overall value score for a neighborhood.
        
        Args:
            affordability: Affordability score (0-100)
            amenities: Amenity score (0-100)
            transit: Transit score (0-100)
            safety: Safety score (0-100)
            growth: Growth potential score (0-100)
            ocean: Ocean proximity score (0-100)
            weights: Custom weights for each factor
            
        Returns:
            Overall value score (0-100)
        """
        if weights is None:
            weights = {
                'affordability': 0.25,
                'amenities': 0.15,
                'transit': 0.15,
                'safety': 0.15,
                'growth': 0.10,
                'ocean': 0.20
            }
        
        score = (
            affordability * weights.get('affordability', 0.25) +
            amenities * weights.get('amenities', 0.15) +
            transit * weights.get('transit', 0.15) +
            safety * weights.get('safety', 0.15) +
            growth * weights.get('growth', 0.10) +
            ocean * weights.get('ocean', 0.20)
        )
        
        return round(score, 2)
    
    def rank_neighborhoods(
        self,
        neighborhoods_df: pd.DataFrame,
        user_preferences: Dict[str, float] = None
    ) -> pd.DataFrame:
        """
        Rank neighborhoods based on value scores.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data and scores
            user_preferences: Optional custom weights for ranking
            
        Returns:
            Ranked DataFrame with value scores
        """
        df = neighborhoods_df.copy()
        
        # Calculate value scores
        df['value_score'] = df.apply(
            lambda row: self.calculate_value_score(
                affordability=row.get('affordability', 50),
                amenities=row.get('amenity_score', 50),
                transit=row.get('transit_score', 50),
                safety=row.get('safety_score', 50),
                growth=row.get('growth_potential', 50),
                ocean=row.get('ocean_proximity_score', 50),
                weights=user_preferences
            ), axis=1
        )
        
        # Rank by value score
        df['rank'] = df['value_score'].rank(ascending=False, method='dense')
        df = df.sort_values('value_score', ascending=False)
        
        return df
    
    def find_best_value_neighborhoods(
        self,
        neighborhoods_df: pd.DataFrame,
        budget: float,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Find neighborhoods with best value within budget.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            budget: Maximum monthly rent budget
            top_n: Number of top neighborhoods to return
            
        Returns:
            Top neighborhoods DataFrame
        """
        # Filter by budget
        if 'median_rent' in neighborhoods_df.columns:
            affordable = neighborhoods_df[
                neighborhoods_df['median_rent'] <= budget
            ].copy()
        else:
            affordable = neighborhoods_df.copy()
        
        # Rank and return top N
        ranked = self.rank_neighborhoods(affordable)
        return ranked.head(top_n)
    
    def compare_neighborhoods(
        self,
        neighborhoods_df: pd.DataFrame,
        neighborhood_names: List[str]
    ) -> pd.DataFrame:
        """
        Compare specific neighborhoods side by side.
        
        Args:
            neighborhoods_df: DataFrame with all neighborhoods
            neighborhood_names: List of neighborhood names to compare
            
        Returns:
            Comparison DataFrame
        """
        comparison = neighborhoods_df[
            neighborhoods_df['name'].isin(neighborhood_names)
        ].copy()
        
        # Select key metrics for comparison
        key_metrics = [
            'name', 'median_rent', 'median_income', 'affordability',
            'amenity_score', 'transit_score', 'safety_score',
            'value_score', 'rank'
        ]
        
        available_metrics = [col for col in key_metrics if col in comparison.columns]
        return comparison[available_metrics]
    
    def analyze_cost_of_living(
        self,
        neighborhoods_df: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Analyze cost of living across neighborhoods.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            
        Returns:
            Dictionary with cost of living analysis
        """
        if neighborhoods_df.empty or 'median_rent' not in neighborhoods_df.columns:
            return {}
        
        analysis = {
            'average_rent': neighborhoods_df['median_rent'].mean(),
            'min_rent': neighborhoods_df['median_rent'].min(),
            'max_rent': neighborhoods_df['median_rent'].max(),
            'rent_std': neighborhoods_df['median_rent'].std(),
            'affordable_pct': (
                (neighborhoods_df['affordability'] >= 70).sum() / 
                len(neighborhoods_df) * 100
            )
        }
        
        # Add income analysis if available
        if 'median_income' in neighborhoods_df.columns:
            analysis['average_income'] = neighborhoods_df['median_income'].mean()
            analysis['income_range'] = (
                neighborhoods_df['median_income'].min(),
                neighborhoods_df['median_income'].max()
            )
        
        return analysis
    
    def identify_emerging_neighborhoods(
        self,
        neighborhoods_df: pd.DataFrame,
        growth_threshold: float = 60.0
    ) -> pd.DataFrame:
        """
        Identify emerging neighborhoods with high growth potential.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            growth_threshold: Minimum growth score to consider
            
        Returns:
            DataFrame with emerging neighborhoods
        """
        if 'growth_potential' not in neighborhoods_df.columns:
            return pd.DataFrame()
        
        emerging = neighborhoods_df[
            neighborhoods_df['growth_potential'] >= growth_threshold
        ].copy()
        
        # Sort by growth potential and affordability
        if 'affordability' in emerging.columns:
            emerging['emerging_score'] = (
                emerging['growth_potential'] * 0.6 +
                emerging['affordability'] * 0.4
            )
            emerging = emerging.sort_values('emerging_score', ascending=False)
        else:
            emerging = emerging.sort_values('growth_potential', ascending=False)
        
        return emerging
    
    def generate_recommendations(
        self,
        neighborhoods_df: pd.DataFrame,
        budget: float,
        priorities: Dict[str, float] = None
    ) -> Dict[str, any]:
        """
        Generate personalized neighborhood recommendations.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            budget: Monthly rent budget
            priorities: User priorities (weights for different factors)
            
        Returns:
            Dictionary with recommendations
        """
        # Find best value options
        best_value = self.find_best_value_neighborhoods(
            neighborhoods_df, budget, top_n=5
        )
        
        # Find emerging neighborhoods
        emerging = self.identify_emerging_neighborhoods(neighborhoods_df)
        
        # Cost of living analysis
        col_analysis = self.analyze_cost_of_living(neighborhoods_df)
        
        recommendations = {
            'best_overall_value': best_value.to_dict('records'),
            'emerging_neighborhoods': emerging.head(5).to_dict('records'),
            'cost_of_living_summary': col_analysis,
            'budget': budget,
            'neighborhoods_analyzed': len(neighborhoods_df)
        }
        
        return recommendations
