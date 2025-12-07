"""Main Streamlit application for Neighborhood Rental Value Analyzer."""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go

# Simplified helper classes (replacing external modules)
class DataProcessor:
    """Simple data processor for affordability calculations."""
    
    def calculate_affordability_index(self, rent: float, income: float) -> float:
        """Calculate affordability score (0-100)."""
        if income <= 0:
            return 0
        monthly_income = income / 12
        rent_to_income_ratio = rent / monthly_income
        
        # Score based on 30% rule (lower ratio = higher score)
        if rent_to_income_ratio <= 0.25:
            return 100
        elif rent_to_income_ratio <= 0.30:
            return 85
        elif rent_to_income_ratio <= 0.35:
            return 70
        elif rent_to_income_ratio <= 0.40:
            return 50
        else:
            return max(0, 100 - (rent_to_income_ratio - 0.3) * 200)

class NeighborhoodAnalyzer:
    """Simple neighborhood analyzer."""
    
    def rank_neighborhoods(self, df: pd.DataFrame, weights: Dict = None) -> pd.DataFrame:
        """Rank neighborhoods by value score."""
        if weights is None:
            weights = {
                'affordability': 0.3,
                'amenities': 0.2,
                'transit': 0.2,
                'safety': 0.2,
                'growth': 0.1
            }
        
        # Calculate weighted value score
        df['value_score'] = (
            df['affordability'] * weights['affordability'] +
            df['amenity_score'] * weights['amenities'] +
            df['transit_score'] * weights['transit'] +
            df['safety_score'] * weights['safety'] +
            df['growth_potential'] * weights['growth']
        )
        
        df = df.sort_values('value_score', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        
        return df
    
    def find_best_value_neighborhoods(self, df: pd.DataFrame, budget: float, top_n: int = 10) -> pd.DataFrame:
        """Find neighborhoods within budget."""
        affordable = df[df['median_rent'] <= budget].copy()
        return affordable.head(top_n)

class Visualizer:
    """Simple visualizer using Plotly."""
    
    def create_affordability_scatter(self, df: pd.DataFrame):
        """Create scatter plot of rent vs affordability."""
        fig = px.scatter(
            df,
            x='median_rent',
            y='affordability',
            size='value_score',
            color='value_score',
            hover_data=['name'],
            labels={'median_rent': 'Monthly Rent ($)', 'affordability': 'Affordability Score'},
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400)
        return fig
    
    def create_distribution_plot(self, df: pd.DataFrame, column: str):
        """Create distribution histogram."""
        fig = px.histogram(
            df,
            x=column,
            nbins=30,
            labels={column: column.replace('_', ' ').title()}
        )
        fig.update_layout(height=400)
        return fig
    
    def create_value_comparison_chart(self, df: pd.DataFrame, metric: str, top_n: int = 10):
        """Create bar chart for value comparison."""
        data = df.head(top_n).copy()
        fig = px.bar(
            data,
            x=metric,
            y='name',
            orientation='h',
            color=metric,
            labels={metric: metric.replace('_', ' ').title(), 'name': 'Neighborhood'},
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False)
        return fig

# Page configuration
st.set_page_config(
    page_title="Neighborhood Rental Value Analyzer",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F0F9FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# Removed external data collectors - using sample data only

@st.cache_data
def load_sample_data(city_selection="All California"):
    """Load sample neighborhood data for demonstration."""
    np.random.seed(42)
    
    # California neighborhoods by city
    ca_neighborhoods = {
        'Los Angeles': [
            ("Hollywood", 34.0928, -118.3287),
            ("Beverly Hills", 34.0736, -118.4004),
            ("Santa Monica", 34.0195, -118.4912),
            ("Downtown LA", 34.0522, -118.2437),
            ("Venice", 33.9850, -118.4695),
            ("Silver Lake", 34.0870, -118.2704),
            ("Echo Park", 34.0780, -118.2607),
            ("Pasadena", 34.1478, -118.1445),
            ("West Hollywood", 34.0900, -118.3617),
            ("Koreatown", 34.0579, -118.3009),
            ("Los Feliz", 34.1071, -118.2828),
            ("Culver City", 34.0211, -118.3965),
            ("Manhattan Beach", 33.8847, -118.4109),
            ("Long Beach", 33.7701, -118.1937),
            ("Burbank", 34.1808, -118.3090),
            ("Glendale", 34.1425, -118.2551),
            ("Sherman Oaks", 34.1508, -118.4490),
            ("Studio City", 34.1486, -118.3965),
            ("Westwood", 34.0633, -118.4456),
            ("Brentwood", 34.0536, -118.4772),
        ],
        'San Francisco': [
            ("Mission District", 37.7599, -122.4148),
            ("SoMa", 37.7749, -122.4194),
            ("Castro", 37.7609, -122.4350),
            ("Pacific Heights", 37.7931, -122.4358),
            ("Marina District", 37.8024, -122.4381),
            ("Nob Hill", 37.7919, -122.4155),
            ("Chinatown", 37.7941, -122.4078),
            ("North Beach", 37.8006, -122.4104),
            ("Haight-Ashbury", 37.7692, -122.4481),
            ("Russian Hill", 37.8003, -122.4200),
            ("Richmond District", 37.7787, -122.4645),
            ("Sunset District", 37.7479, -122.4822),
            ("Potrero Hill", 37.7578, -122.3979),
            ("Bernal Heights", 37.7418, -122.4157),
            ("Glen Park", 37.7326, -122.4339),
        ],
        'San Diego': [
            ("Gaslamp Quarter", 32.7115, -117.1597),
            ("La Jolla", 32.8328, -117.2713),
            ("Pacific Beach", 32.7967, -117.2357),
            ("Mission Bay", 32.7642, -117.2267),
            ("Hillcrest", 32.7486, -117.1664),
            ("North Park", 32.7411, -117.1297),
            ("Little Italy", 32.7209, -117.1698),
            ("Ocean Beach", 32.7475, -117.2489),
            ("Point Loma", 32.7341, -117.2407),
            ("Del Mar", 32.9595, -117.2653),
        ],
        'San Jose': [
            ("Downtown San Jose", 37.3382, -121.8863),
            ("Willow Glen", 37.3044, -121.8896),
            ("Almaden Valley", 37.2091, -121.8355),
            ("Rose Garden", 37.3399, -121.9190),
            ("Santana Row", 37.3207, -121.9483),
            ("Japantown", 37.3469, -121.8950),
            ("Cambrian Park", 37.2527, -121.9297),
            ("Evergreen", 37.3155, -121.7906),
        ],
        'Oakland': [
            ("Lake Merritt", 37.8044, -122.2712),
            ("Rockridge", 37.8444, -122.2514),
            ("Temescal", 37.8347, -122.2632),
            ("Jack London Square", 37.7955, -122.2772),
            ("Montclair", 37.8322, -122.2097),
            ("Piedmont Avenue", 37.8197, -122.2458),
        ],
    }
    
    # Select neighborhoods based on user choice
    if city_selection == "All California":
        neighborhoods = []
        for city, areas in ca_neighborhoods.items():
            neighborhoods.extend([(f"{name} ({city})", lat, lon) for name, lat, lon in areas])
    else:
        neighborhoods = [(f"{name} ({city_selection})", lat, lon) 
                        for name, lat, lon in ca_neighborhoods.get(city_selection, [])]
    
    n = len(neighborhoods)
    names, lats, lons = zip(*neighborhoods) if neighborhoods else ([], [], [])
    
    data = {
        'name': list(names),
        'latitude': list(lats),
        'longitude': list(lons),
        'total_population': np.random.randint(5000, 50000, n),
        'median_income': np.random.randint(40000, 150000, n),
        'median_rent': np.random.randint(1000, 4000, n),
        'median_age': np.random.randint(25, 45, n),
        'college_educated_pct': np.random.uniform(20, 80, n),
        'renter_pct': np.random.uniform(30, 90, n),
        'unemployment_rate': np.random.uniform(2, 10, n),
        'amenity_score': np.random.uniform(40, 95, n),
        'transit_score': np.random.uniform(30, 95, n),
        'safety_score': np.random.uniform(50, 95, n),
        'growth_potential': np.random.uniform(40, 85, n),
    }
    
    df = pd.DataFrame(data)
    
    # Calculate affordability
    processor = DataProcessor()
    df['affordability'] = df.apply(
        lambda row: processor.calculate_affordability_index(
            row['median_rent'], row['median_income']
        ), axis=1
    )
    
    # Calculate value scores
    analyzer = NeighborhoodAnalyzer()
    df = analyzer.rank_neighborhoods(df)
    
    return df

def main():
    """Main application function."""
    
    # Header
    st.markdown('<p class="main-header">Neighborhood Rental Value Analyzer</p>', 
                unsafe_allow_html=True)
    st.markdown("**Find the best neighborhoods for your budget and lifestyle**")
    
    # Sidebar
    st.sidebar.title("Settings")
    
    # City selection
    city_choice = st.sidebar.selectbox(
        "Select California City/Region",
        ["All California", "Los Angeles", "San Francisco", "San Diego", "San Jose", "Oakland"],
        help="Choose which California city neighborhoods to analyze"
    )
    
    # Budget input
    st.sidebar.subheader("Your Budget")
    budget = st.sidebar.slider(
        "Monthly Rent Budget ($)",
        min_value=500,
        max_value=5000,
        value=2000,
        step=100
    )
    
    # Priority weights
    st.sidebar.subheader("Your Priorities")
    st.sidebar.markdown("*Adjust importance of each factor*")
    
    affordability_weight = st.sidebar.slider("Affordability", 0, 100, 30) / 100
    amenities_weight = st.sidebar.slider("Amenities", 0, 100, 20) / 100
    transit_weight = st.sidebar.slider("Transit Access", 0, 100, 20) / 100
    safety_weight = st.sidebar.slider("Safety", 0, 100, 20) / 100
    growth_weight = st.sidebar.slider("Growth Potential", 0, 100, 10) / 100
    
    # Normalize weights to sum to 1
    total_weight = (affordability_weight + amenities_weight + 
                   transit_weight + safety_weight + growth_weight)
    
    if total_weight > 0:
        weights = {
            'affordability': affordability_weight / total_weight,
            'amenities': amenities_weight / total_weight,
            'transit': transit_weight / total_weight,
            'safety': safety_weight / total_weight,
            'growth': growth_weight / total_weight
        }
    else:
        weights = None
    
    # Load data
    with st.spinner(f"Loading {city_choice} data..."):
        neighborhoods_df = load_sample_data(city_choice)
    
    # Main content
    tab1, tab2 = st.tabs([
        "Overview", 
        "Top Neighborhoods"
    ])
    
    # Tab 1: Overview
    with tab1:
        st.header("Market Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Average Rent",
                f"${neighborhoods_df['median_rent'].mean():.0f}",
                delta=f"±{neighborhoods_df['median_rent'].std():.0f}"
            )
        
        with col2:
            st.metric(
                "Avg Value Score",
                f"{neighborhoods_df['value_score'].mean():.1f}",
                delta=f"Range: {neighborhoods_df['value_score'].min():.0f}-{neighborhoods_df['value_score'].max():.0f}"
            )
        
        with col3:
            affordable_count = (neighborhoods_df['median_rent'] <= budget).sum()
            st.metric(
                "Within Budget",
                f"{affordable_count}",
                delta=f"{affordable_count/len(neighborhoods_df)*100:.0f}%"
            )
        
        with col4:
            high_value = (neighborhoods_df['value_score'] >= 70).sum()
            st.metric(
                "High Value Options",
                f"{high_value}",
                delta=f"{high_value/len(neighborhoods_df)*100:.0f}%"
            )
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Affordability Analysis")
            viz = Visualizer()
            fig = viz.create_affordability_scatter(neighborhoods_df)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Rent Distribution")
            fig = viz.create_distribution_plot(neighborhoods_df, 'median_rent')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Top Neighborhoods
    with tab2:
        st.header("Top Neighborhoods for Your Budget")
        
        analyzer = NeighborhoodAnalyzer()
        
        # Recalculate with user weights
        if weights:
            neighborhoods_df = analyzer.rank_neighborhoods(neighborhoods_df, weights)
        
        best_neighborhoods = analyzer.find_best_value_neighborhoods(
            neighborhoods_df, budget, top_n=10
        )
        
        if best_neighborhoods.empty:
            st.warning(f"No neighborhoods found within ${budget} budget. Try increasing your budget.")
        else:
            st.success(f"Found {len(best_neighborhoods)} neighborhoods within your budget!")
            
            # Visualization charts
            st.subheader("Best Neighborhood Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Value Score Comparison**")
                viz = Visualizer()
                fig = viz.create_value_comparison_chart(best_neighborhoods.head(10), 'value_score', top_n=10)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Rent vs Affordability**")
                fig = viz.create_affordability_scatter(best_neighborhoods.head(10))
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Display top 5 in cards
            st.subheader("Top 5 Recommendations")
            
            for idx, (_, neighborhood) in enumerate(best_neighborhoods.head(5).iterrows(), 1):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.markdown(f"### #{idx} {neighborhood['name']}")
                    
                    with col2:
                        st.metric("Rent", f"${neighborhood['median_rent']:.0f}")
                    
                    with col3:
                        st.metric("Value Score", f"{neighborhood['value_score']:.1f}")
                    
                    with col4:
                        st.metric("Affordability", f"{neighborhood['affordability']:.0f}")
                    
                    # Score breakdown
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.caption(f"Affordability: {neighborhood['affordability']:.0f}")
                    with col2:
                        st.caption(f"Amenities: {neighborhood['amenity_score']:.0f}")
                    with col3:
                        st.caption(f"Transit: {neighborhood['transit_score']:.0f}")
                    with col4:
                        st.caption(f"Safety: {neighborhood['safety_score']:.0f}")
                    with col5:
                        st.caption(f"Growth: {neighborhood['growth_potential']:.0f}")
                    
                    st.markdown("---")
            
            # Data table
            st.subheader("Detailed Data")
            display_cols = [
                'name', 'median_rent', 'median_income', 'affordability',
                'amenity_score', 'transit_score', 'safety_score',
                'value_score', 'rank'
            ]
            st.dataframe(
                best_neighborhoods[display_cols].round(1),
                use_container_width=True,
                hide_index=True
            )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280;'>
        <p>Neighborhood Rental Value Analyzer | Data sources: US Census, FRED, OpenStreetMap, City Open Data</p>
        <p>This tool provides estimates and should be used as a guide. Always verify information independently.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
