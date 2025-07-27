import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from collections import Counter
from scipy.stats import zscore
import os

# Set plot style
plt.style.use('seaborn')

def load_logs(file_path):
    """Load and parse server log file into a DataFrame."""
    logs = []
    with open(file_path, 'r') as f:
        for i, line in enumerate(f, 1):
            try:
                timestamp, level, ip, *message = line.strip().split(' ', 3)
                logs.append({
                    'line_number': i,
                    'timestamp': datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S'),
                    'log_level': level,
                    'ip': ip,
                    'message': message[0]
                })
            except:
                continue
    df = pd.DataFrame(logs)
    df['minute'] = df['timestamp'].dt.floor('T')
    df['hour'] = df['timestamp'].dt.floor('H')
    return df

def rule_based_anomalies(df):
    """Detect anomalies using rule-based methods."""
    anomalies = []
    
    # Rule 1: Failed login attempts
    failed_logins = df[df['message'].str.contains('Failed login', case=False)]
    for _, row in failed_logins.iterrows():
        anomalies.append({
            'line_number': row['line_number'],
            'reason': f"Failed login attempt from IP {row['ip']}"
        })
    
    # Rule 2: Repeated IPs (>5 requests in 5 minutes)
    window = 5  # 5-minute window
    ip_counts = df.groupby(['ip', pd.Grouper(key='timestamp', freq=f'{window}T')]).size().reset_index(name='count')
    suspicious_ips = ip_counts[ip_counts['count'] > 5]
    for _, row in suspicious_ips.iterrows():
        ip_logs = df[(df['ip'] == row['ip']) & 
                     (df['timestamp'] >= row['timestamp']) & 
                     (df['timestamp'] < row['timestamp'] + timedelta(minutes=window))]
        for _, log in ip_logs.iterrows():
            anomalies.append({
                'line_number': log['line_number'],
                'reason': f"High request frequency from IP {row['ip']} ({row['count']} in {window} minutes)"
            })
    
    # Rule 3: 404 errors
    errors_404 = df[df['message'].str.contains('404', case=False)]
    for _, row in errors_404.iterrows():
        anomalies.append({
            'line_number': row['line_number'],
            'reason': f"404 error from IP {row['ip']}"
        })
    
    # Rule 4: Brute force attempts (>3 failed logins from same IP in 1 minute)
    brute_force = df[df['message'].str.contains('Failed login', case=False)]
    brute_counts = brute_force.groupby(['ip', pd.Grouper(key='timestamp', freq='1T')]).size().reset_index(name='count')
    brute_suspects = brute_counts[brute_counts['count'] > 3]
    for _, row in brute_suspects.iterrows():
        ip_logs = brute_force[(brute_force['ip'] == row['ip']) & 
                              (brute_force['timestamp'] >= row['timestamp']) & 
                              (brute_force['timestamp'] < row['timestamp'] + timedelta(minutes=1))]
        for _, log in ip_logs.iterrows():
            anomalies.append({
                'line_number': log['line_number'],
                'reason': f"Possible brute force attempt from IP {row['ip']} ({row['count']} failed logins in 1 minute)"
            })
    
    return anomalies

def statistical_anomalies(df):
    """Detect anomalies using statistical methods (z-score for frequency)."""
    anomalies = []
    
    # Frequency per minute
    minute_counts = df.groupby('minute').size().reset_index(name='count')
    minute_counts['z_score'] = zscore(minute_counts['count'])
    high_freq = minute_counts[minute_counts['z_score'].abs() > 2]
    
    for _, row in high_freq.iterrows():
        minute_logs = df[df['minute'] == row['minute']]
        for _, log in minute_logs.iterrows():
            anomalies.append({
                'line_number': log['line_number'],
                'reason': f"Unusual log frequency in minute {row['minute']} (count: {row['count']}, z-score: {row['z_score']:.2f})"
            })
    
    # IQR-based spike detection for ERROR/CRITICAL logs
    error_logs = df[df['log_level'].isin(['ERROR', 'CRITICAL'])]
    if not error_logs.empty:
        error_counts = error_logs.groupby('hour').size().reset_index(name='count')
        Q1 = error_counts['count'].quantile(0.25)
        Q3 = error_counts['count'].quantile(0.75)
        IQR = Q3 - Q1
        outliers = error_counts[error_counts['count'] > Q3 + 1.5 * IQR]
        for _, row in outliers.iterrows():
            hour_logs = error_logs[error_logs['hour'] == row['hour']]
            for _, log in hour_logs.iterrows():
                anomalies.append({
                    'line_number': log['line_number'],
                    'reason': f"High error count in hour {row['hour']} (count: {row['count']}, above IQR threshold)"
                })
    
    return anomalies

def plot_log_levels(df, output_dir='plots'):
    """Plot log level counts over time."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    level_counts = df.groupby(['hour', 'log_level']).size().unstack(fill_value=0)
    plt.figure(figsize=(12, 6))
    for level in level_counts.columns:
        plt.plot(level_counts.index, level_counts[level], label=level, marker='o')
    plt.title('Log Level Counts Over Time')
    plt.xlabel('Hour')
    plt.ylabel('Count')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/log_levels_over_time.png')
    plt.close()

def save_anomalies(anomalies, output_file='flagged_anomalies.txt'):
    """Save detected anomalies to a file."""
    with open(output_file, 'w') as f:
        for anomaly in anomalies:
            f.write(f"Line {anomaly['line_number']}: {anomaly['reason']}\n")

def main():
    """Main function to run the anomaly detection pipeline."""
    # Load logs
    df = load_logs('server_logs.txt')
    
    # Detect anomalies
    rule_anomalies = rule_based_anomalies(df)
    stat_anomalies = statistical_anomalies(df)
    all_anomalies = rule_anomalies + stat_anomalies
    
    # Remove duplicates based on line number
    seen_lines = set()
    unique_anomalies = []
    for anomaly in all_anomalies:
        if anomaly['line_number'] not in seen_lines:
            unique_anomalies.append(anomaly)
            seen_lines.add(anomaly['line_number'])
    
    # Print summary
    print(f"Total Anomalies Detected: {len(unique_anomalies)}")
    print("\nSummary by Reason:")
    reasons = Counter(anomaly['reason'] for anomaly in unique_anomalies)
    for reason, count in reasons.items():
        print(f" - {reason}: {count} occurrences")
    
    # Save anomalies
    save_anomalies(unique_anomalies)
    print(f"\nAnomalies saved to 'flagged_anomalies.txt'")
    
    # Plot log levels
    plot_log_levels(df)
    print("Plot saved in 'plots/log_levels_over_time.png'")

if __name__ == '__main__':
    main()