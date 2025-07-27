Global Geopolitical Risk Dashboard
Setup Instructions

Ensure Python 3.8+ is installed.
Install dependencies:pip install -r requirements.txt


Place app.py and events.csv in the same directory.
Run the dashboard:streamlit run app.py


Open the provided URL (usually http://localhost:8501) in a browser.

Features

Interactive World Map: Visualize geopolitical events with severity-based markers
Dual-Axis Time Series: Track event frequency and average severity over time
Comparative Bar Charts: Analyze severity and count by region and event type
Filterable Data Table: Detailed event log with formatted dates and severity
Advanced Filters: 
Region, Country, Event Type
Date Range with calendar picker
Severity Range slider


Key Metrics: Total events, average severity, high-risk events, and event type count
Responsive Design: Dark-themed sidebar and clean, professional visuals
Reset Filters: One-click reset for all filters

Notes

Uses Streamlit for responsive UI and Plotly for interactive visualizations
Optimized for performance with data caching
Minimal dependencies for quick setup
Custom CSS for enhanced styling
