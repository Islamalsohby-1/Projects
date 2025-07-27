import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from typing import Tuple, Optional

# Cache data loading for performance
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv('events.csv', parse_dates=['Date'])
    df['Severity'] = df['Severity'].astype(float)
    return df

# Process data with advanced filtering
def process_data(
    df: pd.DataFrame,
    region: Optional[str] = None,
    country: Optional[str] = None,
    event_type: Optional[str] = None,
    date_range: Optional[Tuple[datetime, datetime]] = None,
    severity_range: Optional[Tuple[float, float]] = None
) -> pd.DataFrame:
    filtered_df = df.copy()
    
    if region and region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == region]
    if country and country != 'All':
        filtered_df = filtered_df[filtered_df['Country'] == country]
    if event_type and event_type != 'All':
        filtered_df = filtered_df[filtered_df['Event Type'] == event_type]
    if date_range:
        filtered_df = filtered_df[
            (filtered_df['Date'] >= pd.Timestamp(date_range[0])) & 
            (filtered_df['Date'] <= pd.Timestamp(date_range[1]))
        ]
    if severity_range:
        filtered_df = filtered_df[
            (filtered_df['Severity'] >= severity_range[0]) & 
            (filtered_df['Severity'] <= severity_range[1])
        ]
    
    return filtered_df

# Calculate risk metrics
def calculate_risk_metrics(df: pd.DataFrame) -> dict:
    return {
        'total_events': len(df),
        'avg_severity': round(df['Severity'].mean(), 2) if not df.empty else 0,
        'high_risk_events': len(df[df['Severity'] >= 7]),
        'event_types': df['Event Type'].nunique()
    }

# Create enhanced visualizations
def create_map(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter_geo(
        df,
        locations="Country",
        locationmode="country names",
        color="Severity",
        size="Severity",
        hover_name="Description",
        hover_data={
            "Country": True,
            "Date": True,
            "Event Type": True,
            "Severity": True
        },
        projection="natural earth",
        title="Global Geopolitical Risk Map",
        color_continuous_scale=px.colors.sequential.Reds
    )
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
            landcolor="rgb(243, 243, 243)",
            oceancolor="rgb(200, 230, 255)",
            showcountries=True
        ),
        margin={"r":20,"t":50,"l":20,"b":20},
        coloraxis_colorbar_title="Risk Severity"
    )
    return fig

def create_time_series(df: pd.DataFrame) -> go.Figure:
    df_ts = df.groupby(df['Date'].dt.to_period('M')).agg({
        'Severity': ['count', 'mean']
    }).reset_index()
    df_ts.columns = ['Date', 'Count', 'Avg_Severity']
    df_ts['Date'] = df_ts['Date'].dt.to_timestamp()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_ts['Date'], y=df_ts['Count'],
        name='Event Count',
        line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df_ts['Date'], y=df_ts['Avg_Severity'],
        name='Avg Severity',
        yaxis='y2',
        line=dict(color='firebrick', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="Event Frequency and Severity Over Time",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Event Count", titlefont=dict(color="royalblue")),
        yaxis2=dict(
            title="Average Severity",
            titlefont=dict(color="firebrick"),
            overlaying="y",
            side="right"
        ),
        margin={"r":20,"t":50,"l":20,"b":20},
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
    )
    return fig

def create_bar_chart(df: pd.DataFrame, group_by: str = 'Region') -> go.Figure:
    df_bar = df.groupby(group_by).agg({
        'Severity': 'mean',
        'Date': 'count'
    }).reset_index()
    df_bar.columns = [group_by, 'Avg_Severity', 'Count']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_bar[group_by],
        y=df_bar['Avg_Severity'],
        name='Avg Severity',
        marker_color='firebrick'
    ))
    fig.add_trace(go.Bar(
        x=df_bar[group_by],
        y=df_bar['Count'],
        name='Event Count',
        yaxis='y2',
        marker_color='royalblue',
        opacity=0.6
    ))
    
    fig.update_layout(
        title=f"Risk Analysis by {group_by}",
        xaxis=dict(title=group_by),
        yaxis=dict(title="Average Severity", titlefont=dict(color="firebrick")),
        yaxis2=dict(
            title="Event Count",
            titlefont=dict(color="royalblue"),
            overlaying="y",
            side="right"
        ),
        margin={"r":20,"t":50,"l":20,"b":20},
        barmode='group',
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
    )
    return fig

# Main app
def main():
    # Set page config with dark theme
    st.set_page_config(
        page_title="Global Geopolitical Risk Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            background-color: #f0f2f6;
            padding: 20px;
        }
        .stSidebar {
            background-color: #1e1e2f;
            color: white;
        }
        .stButton>button {
            background-color: #ff4b4b;
            color: white;
            border-radius: 5px;
        }
        .metric-card {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Sidebar
    st.sidebar.title("Control Panel")
    
    # Filters
    with st.sidebar:
        regions = ['All'] + sorted(df['Region'].unique().tolist())
        region = st.selectbox("Region", regions, help="Filter by geographic region")
        
        countries = ['All'] + sorted(df['Country'].unique().tolist())
        country = st.selectbox("Country", countries, help="Filter by country")
        
        event_types = ['All'] + sorted(df['Event Type'].unique().tolist())
        event_type = st.selectbox("Event Type", event_types, help="Filter by event type")
        
        min_date = df['Date'].min()
        max_date = df['Date'].max()
        date_range = st.date_input(
            "Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date,
            help="Select date range for events"
        )
        
        severity_range = st.slider(
            "Severity Range",
            min_value=float(df['Severity'].min()),
            max_value=float(df['Severity'].max()),
            value=(float(df['Severity'].min()), float(df['Severity'].max())),
            step=0.5,
            help="Filter by risk severity"
        )
        
        st.markdown("---")
        if st.button("Reset Filters"):
            st.experimental_rerun()

    # Process data
    filtered_df = process_data(df, region, country, event_type, date_range, severity_range)
    
    # Main content
    st.title("Global Geopolitical Risk Dashboard")
    st.markdown("Interactive analysis of global geopolitical events with real-time filtering")
    
    # Metrics
    metrics = calculate_risk_metrics(filtered_df)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><h4>Total Events</h4><h2>{metrics['total_events']}</h2></div>", 
                   unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h4>Avg Severity</h4><h2>{metrics['avg_severity']}</h2></div>", 
                   unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h4>High Risk Events</h4><h2>{metrics['high_risk_events']}</h2></div>", 
                   unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><h4>Event Types</h4><h2>{metrics['event_types']}</h2></div>", 
                   unsafe_allow_html=True)
    
    # Visualizations
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.plotly_chart(create_map(filtered_df), use_container_width=True)
        st.plotly_chart(create_bar_chart(filtered_df, 'Region'), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_time_series(filtered_df), use_container_width=True)
        st.plotly_chart(create_bar_chart(filtered_df, 'Event Type'), use_container_width=True)
    
    # Data table
    st.subheader("Detailed Event Log")
    st.dataframe(
        filtered_df[['Date', 'Country', 'Region', 'Event Type', 'Severity', 'Description']]
        .style.format({'Date': '{:%Y-%m-%d}', 'Severity': '{:.1f}'})
        .set_properties(**{
            'background-color': '#ffffff',
            'border': '1px solid #e0e0e0',
            'padding': '8px'
        }),
        use_container_width=True
    )

if __name__ == "__main__":
    main()