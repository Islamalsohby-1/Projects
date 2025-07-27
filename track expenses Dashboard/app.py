from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import os
from datetime import datetime
import base64
from io import BytesIO

app = Flask(__name__)

# Directory to store uploaded files and generated plots
UPLOAD_FOLDER = 'uploads'
PLOT_FOLDER = 'static/plots'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLOT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home route to upload CSV file
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'expenses.csv')
            file.save(filepath)
            return redirect(url_for('dashboard'))
    return render_template('index.html')

# Dashboard route to display analysis and visualizations
@app.route('/dashboard')
def dashboard():
    try:
        # Read and clean the CSV file
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'expenses.csv'))
        
        # Ensure correct data types
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df = df.dropna()  # Drop rows with invalid data
        
        # Calculate key statistics
        total_spend = df['Amount'].sum()
        category_summary = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        top_categories = category_summary.head(3).to_dict()
        
        # Group by month for bar chart
        df['Month'] = df['Date'].dt.to_period('M')
        monthly_spend = df.groupby('Month')['Amount'].sum().reset_index()
        monthly_spend['Month'] = monthly_spend['Month'].astype(str)
        
        # Generate pie chart using Plotly
        pie_fig = px.pie(values=category_summary.values, names=category_summary.index, 
                        title='Spending by Category')
        pie_chart = pio.to_html(pie_fig, full_html=False)
        
        # Generate bar chart using Plotly
        bar_fig = px.bar(monthly_spend, x='Month', y='Amount', title='Monthly Expenses')
        bar_chart = pio.to_html(bar_fig, full_html=False)
        
        # Generate line chart using Matplotlib for trends
        df['Date'] = df['Date'].dt.date
        daily_spend = df.groupby('Date')['Amount'].sum().reset_index()
        plt.figure(figsize=(10, 5))
        plt.plot(daily_spend['Date'], daily_spend['Amount'], marker='o')
        plt.title('Spending Trend Over Time')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save line chart to buffer and encode as base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        line_chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        # Pass data to template
        return render_template('dashboard.html', 
                            total_spend=total_spend,
                            top_categories=top_categories,
                            pie_chart=pie_chart,
                            bar_chart=bar_chart,
                            line_chart_base64=line_chart_base64)
    
    except Exception as e:
        return render_template('index.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)