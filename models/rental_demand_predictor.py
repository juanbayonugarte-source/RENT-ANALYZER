"""Machine learning model for rental demand prediction."""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import os

class RentalDemandPredictor:
    """Predict rental demand and prices using machine learning."""
    
    def __init__(self):
        """Initialize the rental demand predictor."""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for modeling.
        
        Args:
            df: Input DataFrame with raw features
            
        Returns:
            DataFrame with engineered features
        """
        features = df.copy()
        
        # Select relevant features
        feature_columns = [
            'total_population', 'median_income', 'median_age',
            'college_educated_pct', 'renter_pct', 'unemployment_rate',
            'amenity_score', 'transit_score', 'safety_score',
            'affordability'
        ]
        
        # Use only available columns
        available_features = [col for col in feature_columns if col in features.columns]
        features = features[available_features]
        
        # Handle missing values
        features = features.fillna(features.median())
        
        # Create interaction features
        if 'median_income' in features.columns and 'renter_pct' in features.columns:
            features['income_renter_interaction'] = (
                features['median_income'] * features['renter_pct'] / 100
            )
        
        if 'amenity_score' in features.columns and 'transit_score' in features.columns:
            features['location_quality'] = (
                features['amenity_score'] + features['transit_score']
            ) / 2
        
        self.feature_names = features.columns.tolist()
        return features
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        model_type: str = 'random_forest'
    ) -> Dict[str, float]:
        """
        Train the rental demand prediction model.
        
        Args:
            X: Feature matrix
            y: Target variable (e.g., median_rent)
            model_type: Type of model ('random_forest' or 'gradient_boosting')
            
        Returns:
            Dictionary with training metrics
        """
        # Prepare features
        X_prepared = self.prepare_features(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_prepared, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        else:
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        
        metrics = {
            'train_r2': r2_score(y_train, train_pred),
            'test_r2': r2_score(y_test, test_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
            'test_mae': mean_absolute_error(y_test, test_pred)
        }
        
        self.is_trained = True
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions on new data.
        
        Args:
            X: Feature matrix
            
        Returns:
            Array of predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_prepared = self.prepare_features(X)
        X_scaled = self.scaler.transform(X_prepared)
        
        return self.model.predict(X_scaled)
    
    def predict_demand_level(self, X: pd.DataFrame) -> pd.Series:
        """
        Predict rental demand level (Low, Medium, High).
        
        Args:
            X: Feature matrix
            
        Returns:
            Series with demand levels
        """
        predictions = self.predict(X)
        
        # Categorize into demand levels based on percentiles
        low_threshold = np.percentile(predictions, 33)
        high_threshold = np.percentile(predictions, 67)
        
        demand_levels = pd.Series(['Medium'] * len(predictions))
        demand_levels[predictions < low_threshold] = 'Low'
        demand_levels[predictions > high_threshold] = 'High'
        
        return demand_levels
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance scores.
        
        Returns:
            DataFrame with feature importance
        """
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def save_model(self, filepath: str):
        """Save trained model to disk."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str):
        """Load trained model from disk."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_trained = True
    
    def predict_price_range(
        self,
        X: pd.DataFrame,
        confidence: float = 0.9
    ) -> pd.DataFrame:
        """
        Predict rent price ranges with confidence intervals.
        
        Args:
            X: Feature matrix
            confidence: Confidence level (0-1)
            
        Returns:
            DataFrame with predicted prices and ranges
        """
        if not hasattr(self.model, 'estimators_'):
            # Single prediction
            predictions = self.predict(X)
            std = predictions.std()
            
            results = pd.DataFrame({
                'predicted_rent': predictions,
                'lower_bound': predictions - std,
                'upper_bound': predictions + std
            })
        else:
            # For ensemble models, use estimator variance
            X_prepared = self.prepare_features(X)
            X_scaled = self.scaler.transform(X_prepared)
            
            # Get predictions from all estimators
            all_predictions = np.array([
                estimator.predict(X_scaled) 
                for estimator in self.model.estimators_
            ])
            
            predictions = all_predictions.mean(axis=0)
            std = all_predictions.std(axis=0)
            
            z_score = 1.96 if confidence >= 0.95 else 1.645
            
            results = pd.DataFrame({
                'predicted_rent': predictions,
                'lower_bound': predictions - z_score * std,
                'upper_bound': predictions + z_score * std
            })
        
        return results
