Expense Tracker Dashboard
A Flask-based web application for uploading and analyzing expense data from a CSV file, with visualizations and summary statistics.
Setup Instructions

Clone or create the project structure:

Create a project folder and place the following files:
app.py
templates/index.html
templates/dashboard.html
sample_expenses.csv
requirements.txt


Ensure a static/plots folder exists (created automatically on first run).
Place sample_expenses.csv in an uploads folder (created automatically).


Install dependencies:
pip install -r requirements.txt


Run the application:
python app.py


Access the app:

Open a browser and navigate to http://127.0.0.1:5000.
Upload the sample_expenses.csv file or your own CSV with columns: Date, Category, Amount, Description.



Notes

The CSV file must have headers: Date, Category, Amount, Description.
The app uses Pandas for data processing, Plotly for pie and bar charts, and Matplotlib for the line chart.
Bootstrap is used for basic styling, and Plotly is loaded via CDN for interactive charts.
The app runs in debug mode for development; disable it in production.
