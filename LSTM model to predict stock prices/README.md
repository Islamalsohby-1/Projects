Stock Price Prediction with LSTM
A Python project to predict stock prices using an LSTM model with TensorFlow/Keras.
Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save stock_predictor_lstm.py and requirements.txt.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the Model:
Run: python stock_predictor_lstm.py
The script downloads AAPL stock data via yfinance or uses AAPL.csv if available.
Output includes console metrics (loss, R², trend accuracy) and a plot in the plots/ folder.


View Results:
Check the console for model performance metrics.
Open plots/stock_price_prediction.png for actual vs predicted prices.



Notes

Runs in ~5–10 minutes depending on internet speed and hardware.
Uses yfinance to fetch AAPL data (2020-01-01 to 2025-07-27) or loads from AAPL.csv.
Model uses 60-day sequences to predict the next day's close price.
Requires TensorFlow, pandas, numpy, matplotlib, seaborn, and scikit-learn.
