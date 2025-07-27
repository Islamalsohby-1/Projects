# app.py: Main Dash application for interactive statistical dashboard

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots

# Function to load dataset from CSV
def load_data(dataset_name):
    return pd.read_csv(dataset_name)

# Function to generate descriptive statistics
def generate_summary(df):
    return df.describe(include='all').round(2).to_dict()

# Function to create distribution plots (histogram and box plot)
def plot_distributions(df, column):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram", "Box Plot"))
    
    # Histogram
    fig.add_trace(
        go.Histogram(x=df[column], name="Histogram"),
        row=1, col=1
    )
    
    # Box Plot
    fig.add_trace(
        go.Box(y=df[column], name="Box Plot"),
        row=1, col=2
    )
    
    fig.update_layout(title_text=f"Distribution of {column}", showlegend=False)
    return fig

# Function to create correlation heatmap
def plot_correlation_heatmap(df):
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    corr_matrix = numeric_df.corr()
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation Heatmap")
    return fig

# Function to create scatter or bar plot based on column types
def plot_comparison(df, x_col, y_col):
    if df[x_col].dtype == "object" or len(df[x_col].unique()) < 10:
        # Bar plot for categorical x
        fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
    else:
        # Scatter plot for numerical x
        fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
    return fig

# Initialize Dash app
app = Dash(__name__)

# Load datasets
datasets = {
    "Iris": load_data("dataset1.csv"),
    "Titanic": load_data("dataset2.csv"),
    "Wine": load_data("dataset3.csv")
}

# Layout for the dashboard
app.layout = html.Div([
    # Sidebar for dataset and variable selection
    html.Div([
        html.H2("Statistical Dashboard", style={'text-align': 'center'}),
        html.Label("Select Dataset:"),
        dcc.Dropdown(
            id='dataset-dropdown',
            options=[{'label': name, 'value': name} for name in datasets.keys()],
            value="Iris"
        ),
        html.Label("Select X Variable:"),
        dcc.Dropdown(id='x-column-dropdown'),
        html.Label("Select Y Variable:"),
        dcc.Dropdown(id='y-column-dropdown'),
    ], style={'width': '20%', 'float': 'left', 'padding': '20px'}),
    
    # Main content area for visualizations
    html.Div([
        html.H3(id='dataset-title'),
        html.H4("Descriptive Statistics"),
        dcc.Graph(id='summary-table'),
        html.H4("Distribution Plots"),
        dcc.Graph(id='distribution-plot'),
        html.H4("Correlation Heatmap"),
        dcc.Graph(id='correlation-heatmap'),
        html.H4("Comparison Plot"),
        dcc.Graph(id='comparison-plot'),
    ], style={'width': '75%', 'float': 'right', 'padding': '20px'})
], style={'display': 'flex', 'flex-direction': 'row'})

# Callback to update variable dropdowns based on dataset selection
@app.callback(
    [Output('x-column-dropdown', 'options'),
     Output('y-column-dropdown', 'options'),
     Output('dataset-title', 'children')],
    Input('dataset-dropdown', 'value')
)
def update_dropdowns(dataset_name):
    df = datasets[dataset_name]
    columns = [{'label': col, 'value': col} for col in df.columns]
    return columns, columns, f"Dataset: {dataset_name}"

# Callback to update all visualizations
@app.callback(
    [Output('summary-table', 'figure'),
     Output('distribution-plot', 'figure'),
     Output('correlation-heatmap', 'figure'),
     Output('comparison-plot', 'figure')],
    [Input('dataset-dropdown', 'value'),
     Input('x-column-dropdown', 'value'),
     Input('y-column-dropdown', 'value')]
)
def update_visualizations(dataset_name, x_col, y_col):
    df = datasets[dataset_name]
    
    # Generate summary statistics table
    summary = generate_summary(df)
    table_fig = go.Figure(data=[go.Table(
        header=dict(values=list(summary.keys())),
        cells=dict(values=[summary[col] for col in summary.keys()])
    )])
    
    # Generate distribution plot (using first numerical column if x_col is None)
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    dist_col = x_col if x_col in num_cols else num_cols[0] if len(num_cols) > 0 else df.columns[0]
    dist_fig = plot_distributions(df, dist_col)
    
    # Generate correlation heatmap
    corr_fig = plot_correlation_heatmap(df)
    
    # Generate comparison plot (use first two columns if not selected)
    x_col = x_col if x_col else df.columns[0]
    y_col = y_col if y_col else df.columns[1] if len(df.columns) > 1 else df.columns[0]
    comp_fig = plot_comparison(df, x_col, y_col)
    
    return table_fig, dist_fig, corr_fig, comp_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)