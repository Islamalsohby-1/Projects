import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Set plot style
plt.style.use('seaborn')

def load_data(file_path):
    """Load and preprocess heart rate data from CSV."""
    df = pd.read_csv(file_path, parse_dates=['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.day_name()
    return df

def calculate_stats(df):
    """Calculate basic statistics for each user."""
    stats = df.groupby('user_id').agg({
        'heart_rate': ['mean', 'min', 'max', 'std', 
                      lambda x: x.quantile(0.1),  # Resting rate (10th percentile)
                      lambda x: x.quantile(0.9)]  # Peak rate (90th percentile)
    }).round(2)
    stats.columns = ['mean', 'min', 'max', 'std', 'resting', 'peak']
    return stats

def detect_anomalies(df, threshold=180, spike_threshold=30):
    """Detect anomalies: HR > threshold or sudden spikes."""
    anomalies = []
    for user in df['user_id'].unique():
        user_data = df[df['user_id'] == user].sort_values('timestamp')
        # High heart rate
        high_hr = user_data[user_data['heart_rate'] > threshold]
        # Sudden spikes
        user_data['hr_diff'] = user_data['heart_rate'].diff().abs()
        spikes = user_data[user_data['hr_diff'] > spike_threshold]
        anomalies.append(pd.concat([high_hr, spikes]).drop_duplicates())
    return pd.concat(anomalies) if anomalies else pd.DataFrame()

def plot_time_series(df, output_dir='plots'):
    """Plot heart rate time series for each user."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for user in df['user_id'].unique():
        user_data = df[df['user_id'] == user].sort_values('timestamp')
        plt.figure(figsize=(10, 6))
        plt.plot(user_data['timestamp'], user_data['heart_rate'], label=f'User {user}')
        plt.title(f'Heart Rate Time Series - User {user}')
        plt.xlabel('Timestamp')
        plt.ylabel('Heart Rate (BPM)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{output_dir}/time_series_user_{user}.png')
        plt.close()

def plot_distribution(df, output_dir='plots'):
    """Plot heart rate distribution histogram for each user."""
    for user in df['user_id'].unique():
        user_data = df[df['user_id'] == user]
        plt.figure(figsize=(8, 5))
        sns.histplot(user_data['heart_rate'], bins=20, kde=True)
        plt.title(f'Heart Rate Distribution - User {user}')
        plt.xlabel('Heart Rate (BPM)')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/distribution_user_{user}.png')
        plt.close()

def plot_heatmap(df, output_dir='plots'):
    """Plot heatmap of average heart rate by user and hour."""
    pivot = df.pivot_table(values='heart_rate', index='user_id', columns='hour', aggfunc='mean')
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, cmap='YlOrRd', annot=True, fmt='.1f')
    plt.title('Average Heart Rate by User and Hour')
    plt.xlabel('Hour of Day')
    plt.ylabel('User ID')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/heatmap.png')
    plt.close()

def generate_insights(df):
    """Generate insights based on patterns and anomalies."""
    insights = []
    # High variance by hour
    hourly_variance = df.groupby(['user_id', 'hour'])['heart_rate'].std().unstack()
    for user in hourly_variance.index:
        high_var_hours = hourly_variance.loc[user][hourly_variance.loc[user] > 15]
        if not high_var_hours.empty:
            hours = high_var_hours.index.tolist()
            insights.append(f"User {user} has high variance in heart rate during hours {hours}.")
    
    # Elevated heart rate periods
    hourly_avg = df.groupby(['user_id', 'hour'])['heart_rate'].mean().unstack()
    for user in hourly_avg.index:
        high_hr_hours = hourly_avg.loc[user][hourly_avg.loc[user] > 100]
        if not high_hr_hours.empty:
            hours = high_hr_hours.index.tolist()
            hours_range = f"{min(hours)}-{max(hours)}"
            insights.append(f"User {user} shows elevated heart rate during {hours_range} hours.")
    
    return insights

def main():
    """Main function to run the analysis."""
    # Load data
    df = load_data('heart_rate_data.csv')
    
    # Calculate stats
    stats = calculate_stats(df)
    print("Basic Statistics:")
    print(stats)
    
    # Detect anomalies
    anomalies = detect_anomalies(df)
    if not anomalies.empty:
        print("\nAnomalies Detected:")
        print(anomalies[['user_id', 'timestamp', 'heart_rate', 'hr_diff']])
    
    # Generate insights
    insights = generate_insights(df)
    print("\nInsights:")
    for insight in insights:
        print(insight)
    
    # Generate visualizations
    plot_time_series(df)
    plot_distribution(df)
    plot_heatmap(df)
    print("\nPlots saved in 'plots' directory.")

if __name__ == '__main__':
    main()