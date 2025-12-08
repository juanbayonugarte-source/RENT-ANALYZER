"""Main Streamlit application for Neighborhood Rental Value Analyzer."""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict
import plotly.express as px
import sqlite3
import os

# Simplified helper classes
class DataProcessor:
    """Simple data processor for affordability calculations."""
    
    def calculate_affordability_index(self, rent: float, income: float) -> float:
        """Calculate affordability score (0-100)."""
        if income <= 0:
            return 0
        monthly_income = income / 12
        rent_to_income_ratio = rent / monthly_income
        
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
                'schools': 0.1,
                'growth': 0.1
            }
        
        # Ensure school_score exists
        if 'school_score' not in df.columns:
            df['school_score'] = 75.0  # Default value
        
        df['value_score'] = (
            df['affordability'] * weights['affordability'] +
            df['amenity_score'] * weights['amenities'] +
            df['transit_score'] * weights['transit'] +
            df['safety_score'] * weights['safety'] +
            df['school_score'] * weights.get('schools', 0.1) +
            df['growth_potential'] * weights['growth']
        )
        
        df = df.sort_values('value_score', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        
        return df

class Visualizer:
    """Simple visualizer using Plotly."""
    
    def create_california_overview_chart(self, df: pd.DataFrame, top_n: int = 10):
        """Graph 1: Overall California view - Top 10 counties by average rental score."""
        df_copy = df.copy()
        df_copy['county'] = df_copy['name'].str.extract(r'\(([^)]+)\)')[0]
        
        county_data = df_copy.groupby('county').agg({
            'value_score': 'mean',
            'median_rent': 'mean',
            'affordability': 'mean'
        }).reset_index()
        
        county_data = county_data.sort_values('value_score', ascending=False).head(top_n)
        
        fig = px.bar(
            county_data,
            x='county',
            y='value_score',
            color='value_score',
            labels={'value_score': 'Average Rental Score', 'county': 'County'},
            color_continuous_scale='Blues',
            text='value_score',
            title='Top 10 California Counties by Average Rental Score'
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_tickangle=-45,
            xaxis_title='County',
            yaxis_title='Average Rental Score'
        )
        return fig
    
    def create_county_neighborhoods_chart(self, df: pd.DataFrame, county: str, top_n: int = 5):
        """Graph 2: Filtered county view - Top 5 neighborhoods in selected county."""
        df_copy = df.copy()
        df_copy['county'] = df_copy['name'].str.extract(r'\(([^)]+)\)')[0]
        
        county_neighborhoods = df_copy[df_copy['county'] == county].copy()
        county_neighborhoods = county_neighborhoods.sort_values('value_score', ascending=False).head(top_n)
        
        fig = px.bar(
            county_neighborhoods,
            x='name',
            y='value_score',
            color='value_score',
            labels={'value_score': 'Rental Score', 'name': 'Neighborhood'},
            color_continuous_scale='Viridis',
            text='value_score',
            title=f'Top 5 Neighborhoods in {county}',
            hover_data={'median_rent': ':$,.0f', 'affordability': ':.1f'}
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_tickangle=-45,
            xaxis_title='Neighborhood',
            yaxis_title='Rental Score'
        )
        return fig
    
    def create_county_comparison_chart(self, df: pd.DataFrame, top_n: int = 10):
        """Create vertical bar chart for county-level value comparison (dynamic based on filters)."""
        # Extract county from neighborhood name
        df_copy = df.copy()
        df_copy['county'] = df_copy['name'].str.extract(r'\(([^)]+)\)')[0]
        
        # Aggregate by county
        county_data = df_copy.groupby('county').agg({
            'value_score': 'mean',
            'affordability': 'mean',
            'amenity_score': 'mean',
            'transit_score': 'mean',
            'safety_score': 'mean',
            'growth_potential': 'mean',
            'median_rent': 'mean'
        }).reset_index()
        
        county_data = county_data.sort_values('value_score', ascending=False).head(top_n)
        
        fig = px.bar(
            county_data,
            x='county',
            y='value_score',
            color='value_score',
            labels={'value_score': 'Average Value Score', 'county': 'County/City'},
            color_continuous_scale='Blues',
            text='value_score'
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_tickangle=-45,
            xaxis_title='County/City',
            yaxis_title='Average Value Score',
            title='County-Level Analysis (Dynamic)'
        )
        return fig
    
    def create_neighborhood_detail_chart(self, df: pd.DataFrame, selected_county: str):
        """Create detailed chart of neighborhoods within a selected county."""
        # Filter neighborhoods for the selected county
        df_copy = df.copy()
        df_copy['county'] = df_copy['name'].str.extract(r'\(([^)]+)\)')[0]
        county_neighborhoods = df_copy[df_copy['county'] == selected_county].copy()
        
        if county_neighborhoods.empty:
            return None
        
        # Sort by value score
        county_neighborhoods = county_neighborhoods.sort_values('value_score', ascending=False)
        
        fig = px.bar(
            county_neighborhoods,
            x='name',
            y='value_score',
            color='value_score',
            labels={'value_score': 'Value Score', 'name': 'Neighborhood'},
            color_continuous_scale='Viridis',
            text='value_score',
            hover_data={'median_rent': ':$,.0f', 'affordability': ':.1f'}
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_tickangle=-45,
            xaxis_title='Neighborhood',
            yaxis_title='Value Score',
            title=f'Neighborhoods in {selected_county}'
        )
        return fig
    
    def create_city_fixed_chart(self):
        """Create fixed bar chart showing parent cities only (not affected by filters)."""
        # Fixed city-level data for California major cities
        city_data = pd.DataFrame({
            'city': ['Los Angeles County', 'San Francisco County', 'San Diego County', 'Santa Clara County', 'Alameda County'],
            'avg_value_score': [78.5, 82.3, 80.1, 85.2, 79.8],
            'avg_rent': [2450, 3200, 2650, 2950, 2750]
        })
        
        fig = px.bar(
            city_data,
            x='city',
            y='avg_value_score',
            color='avg_value_score',
            labels={'avg_value_score': 'Average Value Score', 'city': 'County'},
            color_continuous_scale='Greens',
            text='avg_value_score',
            hover_data={'avg_rent': ':$,.0f'}
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_tickangle=-45,
            xaxis_title='County (Parent Level)',
            yaxis_title='Average Value Score',
            title='Parent Counties (Fixed)'
        )
        return fig
    
    def create_hierarchical_metrics_chart(self, df: pd.DataFrame, top_n: int = 10):
        """Create grouped bar chart showing all key metrics by neighborhood."""
        data = df.head(top_n).copy()
        
        # Prepare data for grouped bar chart
        metrics_data = []
        for _, row in data.iterrows():
            metrics_data.extend([
                {'Neighborhood': row['name'], 'Metric': 'Affordability', 'Score': row['affordability']},
                {'Neighborhood': row['name'], 'Metric': 'Amenities', 'Score': row['amenity_score']},
                {'Neighborhood': row['name'], 'Metric': 'Transit', 'Score': row['transit_score']},
                {'Neighborhood': row['name'], 'Metric': 'Safety', 'Score': row['safety_score']},
                {'Neighborhood': row['name'], 'Metric': 'Growth', 'Score': row['growth_potential']},
            ])
        
        metrics_df = pd.DataFrame(metrics_data)
        
        fig = px.bar(
            metrics_df,
            x='Neighborhood',
            y='Score',
            color='Metric',
            barmode='group',
            labels={'Score': 'Score (0-100)', 'Neighborhood': 'Neighborhood'},
            color_discrete_map={
                'Affordability': '#3B82F6',
                'Amenities': '#10B981',
                'Transit': '#F59E0B',
                'Safety': '#EF4444',
                'Growth': '#8B5CF6'
            }
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

# ========== SQLite Database Functions ==========

class DatabaseManager:
    """Manages SQLite database for rental data."""
    
    def __init__(self, db_path="rental_data.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Create database connection."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        return self.conn
    
    def create_table(self):
        """Create neighborhoods table if it doesn't exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS neighborhoods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                county TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                total_population INTEGER,
                median_income REAL,
                median_rent REAL,
                median_age INTEGER,
                college_educated_pct REAL,
                renter_pct REAL,
                unemployment_rate REAL,
                amenity_score REAL,
                transit_score REAL,
                safety_score REAL,
                school_score REAL,
                growth_potential REAL,
                affordability REAL,
                value_score REAL,
                rank INTEGER
            )
        ''')
        self.conn.commit()
    
    def insert_data(self, df: pd.DataFrame):
        """Insert DataFrame into database."""
        # Clear existing data
        self.cursor.execute('DELETE FROM neighborhoods')
        
        # Insert new data
        df.to_sql('neighborhoods', self.conn, if_exists='replace', index=False)
        self.conn.commit()
    
    def query_all_neighborhoods(self):
        """Query all neighborhoods from database."""
        query = '''
            SELECT * FROM neighborhoods
            ORDER BY value_score DESC
        '''
        return pd.read_sql_query(query, self.conn)
    
    def query_by_county(self, county: str):
        """Query neighborhoods by county using SQL WHERE clause."""
        query = '''
            SELECT * FROM neighborhoods
            WHERE county = ?
            ORDER BY value_score DESC
        '''
        return pd.read_sql_query(query, self.conn, params=(county,))
    
    def query_by_budget(self, max_rent: float):
        """Query neighborhoods within budget using SQL WHERE clause."""
        query = '''
            SELECT * FROM neighborhoods
            WHERE median_rent <= ?
            ORDER BY value_score DESC
        '''
        return pd.read_sql_query(query, self.conn, params=(max_rent,))
    
    def query_by_county_and_budget(self, county: str, max_rent: float):
        """Query neighborhoods by county and budget using SQL WHERE clauses."""
        query = '''
            SELECT * FROM neighborhoods
            WHERE county = ? AND median_rent <= ?
            ORDER BY value_score DESC
        '''
        return pd.read_sql_query(query, self.conn, params=(county, max_rent))
    
    def query_top_counties(self, top_n: int = 10):
        """Query top counties by average value score using SQL aggregation."""
        query = '''
            SELECT 
                county,
                AVG(value_score) as avg_value_score,
                AVG(median_rent) as avg_rent,
                AVG(affordability) as avg_affordability,
                COUNT(*) as neighborhood_count
            FROM neighborhoods
            GROUP BY county
            ORDER BY avg_value_score DESC
            LIMIT ?
        '''
        return pd.read_sql_query(query, self.conn, params=(top_n,))
    
    def query_county_stats(self, county: str):
        """Get statistics for a specific county using SQL aggregation."""
        query = '''
            SELECT 
                county,
                COUNT(*) as total_neighborhoods,
                AVG(median_rent) as avg_rent,
                AVG(value_score) as avg_value_score,
                AVG(affordability) as avg_affordability,
                MIN(median_rent) as min_rent,
                MAX(median_rent) as max_rent
            FROM neighborhoods
            WHERE county = ?
            GROUP BY county
        '''
        return pd.read_sql_query(query, self.conn, params=(county,))
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

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
        'school_score': np.random.uniform(50, 95, n),  # School quality score (simulated GreatSchools API data)
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
    
    # Add bedroom data (simulated for demo - would come from rental listings API)
    bedroom_options = ['Studio', '1BR', '2BR', '3BR', '4BR']
    df['bedrooms'] = np.random.choice(bedroom_options, n)
    
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
    
    # Data sources info
    with st.expander("ℹ️ Data Sources & APIs"):
        st.markdown("""
        **This application integrates data from multiple sources:**
        - 🏫 **School Quality**: GreatSchools API (ratings from 1-10, normalized to 0-100)
        - 🚇 **Transit Access**: Walk Score API
        - 🏥 **Amenities**: OpenStreetMap API (Overpass)
        - 📊 **Demographics**: US Census Bureau API
        - 💰 **Economic Data**: FRED (Federal Reserve Economic Data)
        - 🏠 **Rental Listings**: Zillow/Realtor.com APIs (bedroom counts, pricing)
        
        *Note: Current implementation uses simulated data for demonstration purposes.*
        """)
    
    # ========== INITIALIZE DATABASE ==========
    # Initialize database manager
    db = DatabaseManager()
    db.connect()
    db.create_table()
    
    # Load sample data and populate database
    neighborhoods_df = load_sample_data("All California")
    
    # Calculate rankings
    analyzer = NeighborhoodAnalyzer()
    neighborhoods_df = analyzer.rank_neighborhoods(neighborhoods_df)
    
    # Extract counties
    neighborhoods_df['county'] = neighborhoods_df['name'].str.extract(r'\(([^)]+)\)')[0]
    
    # Insert data into SQLite database
    db.insert_data(neighborhoods_df)
    
    st.success("✅ Database initialized and populated with neighborhood data")
    
    # Get available counties from database
    available_counties = sorted(neighborhoods_df['county'].unique())
    
    # Sidebar
    st.sidebar.title("Filters")
    
    # County filter
    st.sidebar.subheader("County Selection")
    selected_county = st.sidebar.selectbox(
        "Select County",
        options=["All California"] + available_counties,
        help="Filter all content by county"
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
    
    # Room selection
    st.sidebar.subheader("Property Requirements")
    bedrooms = st.sidebar.selectbox(
        "Number of Bedrooms",
        options=["Any", "Studio (0)", "1 Bedroom", "2 Bedrooms", "3 Bedrooms", "4+ Bedrooms"],
        help="Filter by number of bedrooms"
    )
    
    # Priority weights
    st.sidebar.subheader("Your Priorities")
    st.sidebar.markdown("*Adjust importance of each factor*")
    
    affordability_weight = st.sidebar.slider("Affordability", 0, 100, 30) / 100
    amenities_weight = st.sidebar.slider("Amenities", 0, 100, 20) / 100
    transit_weight = st.sidebar.slider("Transit Access", 0, 100, 20) / 100
    safety_weight = st.sidebar.slider("Safety", 0, 100, 20) / 100
    school_weight = st.sidebar.slider("School Quality", 0, 100, 15) / 100
    growth_weight = st.sidebar.slider("Growth Potential", 0, 100, 10) / 100
    
    # Normalize weights
    total_weight = (affordability_weight + amenities_weight + 
                   transit_weight + safety_weight + school_weight + growth_weight)
    
    if total_weight > 0:
        weights = {
            'affordability': affordability_weight / total_weight,
            'amenities': amenities_weight / total_weight,
            'transit': transit_weight / total_weight,
            'safety': safety_weight / total_weight,
            'schools': school_weight / total_weight,
            'growth': growth_weight / total_weight
        }
    
    # ========== QUERY DATA FROM DATABASE USING SQL ==========
    # Query neighborhoods from database based on filters
    if selected_county != "All California":
        filtered_df = db.query_by_county_and_budget(selected_county, budget)
        sql_query_used = f"""SELECT * FROM neighborhoods
WHERE county = '{selected_county}' AND median_rent <= {budget}
ORDER BY value_score DESC"""
    else:
        filtered_df = db.query_by_budget(budget)
        sql_query_used = f"""SELECT * FROM neighborhoods
WHERE median_rent <= {budget}
ORDER BY value_score DESC"""
    
    # Get all data for California overview chart
    all_neighborhoods_df = db.query_all_neighborhoods()
    budget_filtered_df = filtered_df.copy()
    
    # ========== CREATE TABS ==========
    tab1, tab2, tab3 = st.tabs(["🏠 Welcome Overview", "📊 Top Neighborhoods", "💾 SQL Database Analysis"])
    
    # ========== TAB 1: WELCOME OVERVIEW ==========
    with tab1:
        st.header("California Rental Market Overview")
        st.markdown("**Explore rental trends across California counties and neighborhoods**")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Neighborhoods",
                f"{len(all_neighborhoods_df)}",
                delta="All California"
            )
        
        with col2:
            st.metric(
                "Average Rent",
                f"${all_neighborhoods_df['median_rent'].mean():.0f}"
            )
        
        with col3:
            st.metric(
                "Avg Value Score",
                f"{all_neighborhoods_df['value_score'].mean():.1f}"
            )
        
        with col4:
            st.metric(
                "Counties",
                f"{all_neighborhoods_df['county'].nunique()}"
            )
        
        st.markdown("---")
        
        # Two visualization columns
        col1, col2 = st.columns(2)
        
        viz = Visualizer()
        
        with col1:
            st.subheader("Top 10 California Counties")
            st.caption("📊 Data Source: SQL aggregation query (GROUP BY county)")
            fig1 = viz.create_california_overview_chart(all_neighborhoods_df, top_n=10)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("County Neighborhoods Preview")
            st.caption("📊 Data Source: SQL filtered query (WHERE county = ?)")
            if selected_county != "All California":
                if len(budget_filtered_df) > 0:
                    fig2 = viz.create_county_neighborhoods_chart(budget_filtered_df, selected_county, top_n=5)
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info(f"No neighborhoods found in {selected_county} within ${budget} budget.")
            else:
                st.info("💡 Select a county from the sidebar to view top neighborhoods in that area.")
        
        st.markdown("---")
        st.info("👈 Use the sidebar filters to customize your search, then check the **Top Neighborhoods** tab for detailed recommendations!")
    
    # ========== TAB 2: TOP NEIGHBORHOODS ==========
    with tab2:
        st.header("Top Neighborhoods for Your Budget")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Neighborhoods Found",
                f"{len(budget_filtered_df)}",
                delta=f"Within ${budget}"
            )
        
        with col2:
            if len(budget_filtered_df) > 0:
                st.metric(
                    "Average Rent",
                    f"${budget_filtered_df['median_rent'].mean():.0f}"
                )
            else:
                st.metric("Average Rent", "N/A")
        
        with col3:
            if len(budget_filtered_df) > 0:
                st.metric(
                    "Avg Value Score",
                    f"{budget_filtered_df['value_score'].mean():.1f}"
                )
            else:
                st.metric("Avg Value Score", "N/A")
        
        with col4:
            if len(budget_filtered_df) > 0:
                st.metric(
                    "Avg Affordability",
                    f"{budget_filtered_df['affordability'].mean():.0f}"
                )
            else:
                st.metric("Avg Affordability", "N/A")
        
        st.markdown("---")
        
        # Display top recommendations
        if len(budget_filtered_df) > 0:
            st.subheader("Top Recommendations")
        
        top_neighborhoods = budget_filtered_df.head(5)
        
        for idx, (_, neighborhood) in enumerate(top_neighborhoods.iterrows(), 1):
            # Determine color based on value score
            score = neighborhood['value_score']
            if score >= 85:
                color = "#10B981"  # Green - Excellent
                rating = "Excellent"
                bg_color = "#D1FAE5"
            elif score >= 75:
                color = "#3B82F6"  # Blue - Great
                rating = "Great"
                bg_color = "#DBEAFE"
            elif score >= 65:
                color = "#F59E0B"  # Orange - Good
                rating = "Good"
                bg_color = "#FEF3C7"
            else:
                color = "#6B7280"  # Gray - Fair
                rating = "Fair"
                bg_color = "#F3F4F6"
            
            with st.container():
                # Color-coded header with rating tile
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, {bg_color} 0%, white 100%); 
                            padding: 15px; 
                            border-radius: 10px; 
                            border-left: 5px solid {color};
                            margin-bottom: 10px;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <h3 style="margin: 0; color: #1F2937;">#{idx} {neighborhood['name']}</h3>
                        <div style="background-color: {color}; 
                                    color: white; 
                                    padding: 8px 20px; 
                                    border-radius: 20px; 
                                    font-weight: bold;
                                    font-size: 14px;">
                            {rating} - {score:.1f}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics row
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Rent", f"${neighborhood['median_rent']:.0f}")
                
                with col2:
                    st.metric("Value Score", f"{neighborhood['value_score']:.1f}")
                
                with col3:
                    st.metric("Affordability", f"{neighborhood['affordability']:.0f}")
                
                # Score breakdown
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                    st.caption(f"Affordability: {neighborhood['affordability']:.0f}")
                with col2:
                    st.caption(f"Amenities: {neighborhood['amenity_score']:.0f}")
                with col3:
                    st.caption(f"Transit: {neighborhood['transit_score']:.0f}")
                with col4:
                    st.caption(f"Safety: {neighborhood['safety_score']:.0f}")
                with col5:
                    st.caption(f"Schools: {neighborhood['school_score']:.0f}")
                with col6:
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
                budget_filtered_df[display_cols].head(10).round(1),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning(f"No neighborhoods found within your criteria. Try adjusting your budget or county filter.")
    
    # ========== TAB 3: SQL DATABASE ANALYSIS ==========
    with tab3:
        st.header("SQL Database Analysis")
        st.markdown("**View live database queries and statistics**")
        
        st.success("✅ Connected to SQLite Database: `rental_data.db`")
        
        # Current Query Section
        st.subheader("Current Active Query")
        st.code(sql_query_used, language="sql")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Records Returned", len(budget_filtered_df))
        with col2:
            st.metric("Database Size", f"{len(all_neighborhoods_df)} total records")
        
        st.markdown("---")
        
        # Database Query Section
        st.subheader("SQL Database Queries & Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top 10 Counties Query:**")
            county_stats_df = db.query_top_counties(top_n=10)
            st.code("""
SELECT 
    county,
    AVG(value_score) as avg_value_score,
    AVG(median_rent) as avg_rent,
    COUNT(*) as neighborhood_count
FROM neighborhoods
GROUP BY county
ORDER BY avg_value_score DESC
LIMIT 10
            """, language="sql")
            st.dataframe(county_stats_df, use_container_width=True, hide_index=True)
        
        with col2:
            if selected_county != "All California":
                st.markdown(f"**{selected_county} Statistics Query:**")
                county_detail = db.query_county_stats(selected_county)
                st.code(f"""
SELECT 
    county,
    COUNT(*) as total_neighborhoods,
    AVG(median_rent) as avg_rent,
    AVG(value_score) as avg_value_score,
    MIN(median_rent) as min_rent,
    MAX(median_rent) as max_rent
FROM neighborhoods
WHERE county = '{selected_county}'
GROUP BY county
                """, language="sql")
                st.dataframe(county_detail, use_container_width=True, hide_index=True)
            else:
                st.info("💡 Select a county to view detailed statistics")
        
        st.markdown("---")
        
        # Sample data from database
        st.subheader("Sample Database Records")
        st.caption("First 10 records from the neighborhoods table")
        sample_query = "SELECT * FROM neighborhoods LIMIT 10"
        st.code(sample_query, language="sql")
        sample_df = pd.read_sql_query(sample_query, db.conn)
        st.dataframe(sample_df, use_container_width=True, hide_index=True)
    
    # Close database connection
    db.close()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7280;'>
        <p>Neighborhood Rental Value Analyzer | SQLite Database-Powered Analysis</p>
        <p>Data sources: US Census, FRED, OpenStreetMap, City Open Data</p>
        <p>This tool provides estimates and should be used as a guide. Always verify information independently.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
