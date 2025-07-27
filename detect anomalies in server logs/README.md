Server Log Anomaly Detector
A Python project to detect anomalies in server logs using rule-based and statistical methods.
Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save log_analyzer.py, server_logs.txt, and requirements.txt.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the Analysis:
Run: python log_analyzer.py
Output includes a console summary, flagged_anomalies.txt with detected issues, and a plot in plots/log_levels_over_time.png.


View Results:
Check the console for a summary of detected anomalies.
Open flagged_anomalies.txt for details (line numbers and reasons).
View plots/log_levels_over_time.png for log level trends.



Notes

Runs in ~5 minutes with a standard Python setup.
Analyzes 500+ log lines for failed logins, 404 errors, brute force attempts, high request frequencies, and statistical anomalies (z-score, IQR).
Add new logs to server_logs.txt with format: [YYYY-MM-DDTHH:MM:SS] [LEVEL] [IP] [MESSAGE].
Plot shows log level counts over time, saved in the plots/ directory.
