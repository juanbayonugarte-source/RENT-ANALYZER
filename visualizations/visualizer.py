"""Visualization utilities for the rental value analyzer."""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional
import folium
from folium import plugins

class Visualizer:
    """Create visualizations for neighborhood data."""
    
    @staticmethod
    def create_value_comparison_chart(
        neighborhoods_df: pd.DataFrame,
        metric: str = 'value_score',
        top_n: int = 10
    ) -> go.Figure:
        """
        Create horizontal bar chart comparing neighborhoods.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            metric: Metric to compare
            top_n: Number of neighborhoods to show
            
        Returns:
            Plotly figure
        """
        df = neighborhoods_df.nlargest(top_n, metric).sort_values(metric)
        
        fig = go.Figure(go.Bar(
            x=df[metric],
            y=df['name'] if 'name' in df.columns else df.index,
            orientation='h',
            marker=dict(
                color=df[metric],
                colorscale='Viridis',
                showscale=True
            ),
            text=df[metric].round(1),
            textposition='auto',
        ))
        
        fig.update_layout(
            title=f'Top {top_n} Neighborhoods by {metric.replace("_", " ").title()}',
            xaxis_title=metric.replace('_', ' ').title(),
            yaxis_title='Neighborhood',
            height=400,
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_affordability_scatter(
        neighborhoods_df: pd.DataFrame
    ) -> go.Figure:
        """
        Create scatter plot of rent vs income.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            
        Returns:
            Plotly figure
        """
        fig = px.scatter(
            neighborhoods_df,
            x='median_income',
            y='median_rent',
            size='total_population' if 'total_population' in neighborhoods_df.columns else None,
            color='affordability' if 'affordability' in neighborhoods_df.columns else None,
            hover_name='name' if 'name' in neighborhoods_df.columns else None,
            hover_data=['value_score'] if 'value_score' in neighborhoods_df.columns else None,
            title='Affordability Analysis: Rent vs Income',
            labels={
                'median_income': 'Median Annual Income ($)',
                'median_rent': 'Median Monthly Rent ($)',
                'affordability': 'Affordability Score'
            },
            color_continuous_scale='RdYlGn'
        )
        
        # Add 30% rent-to-income guideline
        if 'median_income' in neighborhoods_df.columns:
            income_range = neighborhoods_df['median_income'].dropna()
            if len(income_range) > 0:
                x_range = [income_range.min(), income_range.max()]
                y_range = [x * 0.3 / 12 for x in x_range]  # 30% annual to monthly
                
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_range,
                    mode='lines',
                    name='30% Income Guideline',
                    line=dict(color='red', dash='dash')
                ))
        
        fig.update_layout(template='plotly_white', height=500)
        return fig
    
    @staticmethod
    def create_spider_chart(
        neighborhood_data: Dict[str, float],
        neighborhood_name: str
    ) -> go.Figure:
        """
        Create spider/radar chart for neighborhood characteristics.
        
        Args:
            neighborhood_data: Dictionary with score data
            neighborhood_name: Name of the neighborhood
            
        Returns:
            Plotly figure
        """
        categories = [
            'Affordability',
            'Amenities',
            'Transit',
            'Safety',
            'Growth Potential'
        ]
        
        values = [
            neighborhood_data.get('affordability', 0),
            neighborhood_data.get('amenity_score', 0),
            neighborhood_data.get('transit_score', 0),
            neighborhood_data.get('safety_score', 0),
            neighborhood_data.get('growth_potential', 0)
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=neighborhood_name,
            line=dict(color='rgb(0, 128, 128)')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title=f'Neighborhood Profile: {neighborhood_name}',
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def create_heatmap(
        neighborhoods_df: pd.DataFrame,
        metrics: List[str]
    ) -> go.Figure:
        """
        Create correlation heatmap of metrics.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            metrics: List of metrics to include
            
        Returns:
            Plotly figure
        """
        available_metrics = [m for m in metrics if m in neighborhoods_df.columns]
        
        if not available_metrics:
            return go.Figure()
        
        corr_matrix = neighborhoods_df[available_metrics].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title='Correlation Heatmap of Neighborhood Metrics',
            template='plotly_white',
            height=500,
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    
    @staticmethod
    def create_distribution_plot(
        neighborhoods_df: pd.DataFrame,
        metric: str
    ) -> go.Figure:
        """
        Create distribution plot for a metric.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            metric: Metric to plot
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=neighborhoods_df[metric],
            name=metric,
            nbinsx=30,
            marker=dict(color='rgb(0, 128, 128)')
        ))
        
        # Add mean line
        mean_val = neighborhoods_df[metric].mean()
        fig.add_vline(
            x=mean_val,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_val:.1f}"
        )
        
        fig.update_layout(
            title=f'Distribution of {metric.replace("_", " ").title()}',
            xaxis_title=metric.replace('_', ' ').title(),
            yaxis_title='Count',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_neighborhood_map(
        neighborhoods_df: pd.DataFrame,
        center_lat: float,
        center_lon: float,
        color_by: str = 'value_score'
    ) -> folium.Map:
        """
        Create interactive map of neighborhoods.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            center_lat: Center latitude
            center_lon: Center longitude
            color_by: Metric to use for coloring
            
        Returns:
            Folium map
        """
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Add markers for each neighborhood
        if 'latitude' in neighborhoods_df.columns and 'longitude' in neighborhoods_df.columns:
            for idx, row in neighborhoods_df.iterrows():
                # Determine marker color based on score
                if color_by in row:
                    score = row[color_by]
                    if score >= 75:
                        color = 'green'
                    elif score >= 50:
                        color = 'orange'
                    else:
                        color = 'red'
                else:
                    color = 'blue'
                
                # Create popup text
                popup_text = f"""
                <b>{row.get('name', 'Unknown')}</b><br>
                Median Rent: ${row.get('median_rent', 'N/A')}<br>
                Value Score: {row.get('value_score', 'N/A')}<br>
                Affordability: {row.get('affordability', 'N/A')}<br>
                Transit Score: {row.get('transit_score', 'N/A')}
                """
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=8,
                    popup=folium.Popup(popup_text, max_width=200),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7
                ).add_to(m)
        
        # Add heat map layer if enough data
        if len(neighborhoods_df) > 10 and 'latitude' in neighborhoods_df.columns:
            heat_data = [
                [row['latitude'], row['longitude'], row.get(color_by, 50)/100]
                for idx, row in neighborhoods_df.iterrows()
                if pd.notna(row.get('latitude'))
            ]
            
            if heat_data:
                plugins.HeatMap(heat_data, radius=15).add_to(m)
        
        return m
    
    @staticmethod
    def create_comparison_table(
        neighborhoods_df: pd.DataFrame,
        neighborhood_names: List[str]
    ) -> go.Figure:
        """
        Create comparison table for selected neighborhoods.
        
        Args:
            neighborhoods_df: DataFrame with neighborhood data
            neighborhood_names: List of neighborhoods to compare
            
        Returns:
            Plotly figure
        """
        comparison = neighborhoods_df[
            neighborhoods_df['name'].isin(neighborhood_names)
        ]
        
        metrics = [
            'median_rent', 'median_income', 'affordability',
            'amenity_score', 'transit_score', 'safety_score', 'value_score'
        ]
        
        available_metrics = [m for m in metrics if m in comparison.columns]
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Metric'] + neighborhood_names,
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12, color='black')
            ),
            cells=dict(
                values=[
                    [m.replace('_', ' ').title() for m in available_metrics]
                ] + [
                    comparison[comparison['name'] == name][available_metrics].values[0].round(1)
                    for name in neighborhood_names
                ],
                fill_color='lavender',
                align='left'
            )
        )])
        
        fig.update_layout(
            title='Neighborhood Comparison',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_trend_chart(
        time_series_df: pd.DataFrame,
        metric: str,
        title: str = None
    ) -> go.Figure:
        """
        Create time series trend chart.
        
        Args:
            time_series_df: DataFrame with time series data
            metric: Metric to plot
            title: Chart title
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=time_series_df['date'],
            y=time_series_df[metric],
            mode='lines+markers',
            name=metric,
            line=dict(color='rgb(0, 128, 128)', width=2)
        ))
        
        fig.update_layout(
            title=title or f'{metric.replace("_", " ").title()} Over Time',
            xaxis_title='Date',
            yaxis_title=metric.replace('_', ' ').title(),
            template='plotly_white',
            height=400,
            hovermode='x unified'
        )
        
        return fig
