Heart Rate Analysis Project
A Python project to analyze heart rate data, perform time-series analysis, detect anomalies, and visualize patterns.
Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save heart_rate_analysis.py, heart_rate_data.csv, and requirements.txt.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the Analysis:
Run: python heart_rate_analysis.py
Output includes console stats, insights, and plots saved in a plots/ folder.


View Results:
Check the console for statistics, anomalies, and insights.
Open the plots/ folder for time series, distribution, and heatmap visualizations.



Adding New Data

Edit heart_rate_data.csv to add new entries.
Format: user_id,timestamp,heart_rate (e.g., 1,2025-07-20 08:00:00,72).
Ensure timestamps are in YYYY-MM-DD HH:MM:SS format and heart rates are integers.

Notes

Runs in ~5 minutes with a standard Python setup.
Uses pandas for data handling, matplotlib/seaborn for visualization, and numpy for calculations.
Outputs plots for each user (time series and distribution) and a heatmap for hourly patterns.

