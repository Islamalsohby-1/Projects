import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import r2_score
import os

# Set plot style
plt.style.use('seaborn')

def load_stock_data(ticker='AAPL', start_date='2020-01-01', end_date='2025-07-27'):
    """Load stock data from Yahoo Finance or CSV if available."""
    if os.path.exists(f'{ticker}.csv'):
        df = pd.read_csv(f'{ticker}.csv', parse_dates=['Date'], index_col='Date')
    else:
        df = yf.download(ticker, start=start_date, end=end_date)
        df.to_csv(f'{ticker}.csv')
    return df[['Close']]

def preprocess_data(df, sequence_length=60, train_split=0.8):
    """Preprocess stock data: normalize and create sequences."""
    # Normalize data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[['Close']].values)
    
    # Create sequences
    X, y = [], []
    for i in range(sequence_length, len(scaled_data)):
        X.append(scaled_data[i-sequence_length:i, 0])
        y.append(scaled_data[i, 0])
    
    X, y = np.array(X), np.array(y)
    
    # Split into train and test
    train_size = int(len(X) * train_split)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Reshape for LSTM [samples, time steps, features]
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
    
    return X_train, X_test, y_train, y_test, scaler

def build_lstm_model(sequence_length):
    """Build and compile LSTM model."""
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    return model

def train_model(model, X_train, y_train, epochs=25, batch_size=32):
    """Train the LSTM model."""
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, 
                       validation_split=0.1, verbose=1)
    return history

def evaluate_model(model, X_train, X_test, y_train, y_test, scaler, df):
    """Evaluate model and calculate metrics."""
    # Make predictions
    train_predict = model.predict(X_train)
    test_predict = model.predict(X_test)
    
    # Inverse transform predictions
    train_predict = scaler.inverse_transform(train_predict)
    y_train_inv = scaler.inverse_transform([y_train])
    test_predict = scaler.inverse_transform(test_predict)
    y_test_inv = scaler.inverse_transform([y_test])
    
    # Calculate R² score
    train_r2 = r2_score(y_train_inv.T, train_predict)
    test_r2 = r2_score(y_test_inv.T, test_predict)
    
    # Calculate trend accuracy
    train_trend = np.sign(np.diff(train_predict.flatten())) == np.sign(np.diff(y_train_inv.flatten()))
    test_trend = np.sign(np.diff(test_predict.flatten())) == np.sign(np.diff(y_test_inv.flatten()))
    train_trend_acc = np.mean(train_trend) * 100
    test_trend_acc = np.mean(test_trend) * 100
    
    # Get losses
    train_loss = model.evaluate(X_train, y_train, verbose=0)
    test_loss = model.evaluate(X_test, y_test, verbose=0)
    
    return train_predict, test_predict, train_r2, test_r2, train_trend_acc, test_trend_acc, train_loss, test_loss

def plot_results(df, train_predict, test_predict, sequence_length, output_dir='plots'):
    """Plot actual vs predicted stock prices."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Prepare data for plotting
    train_plot = np.empty_like(df['Close'].values)
    train_plot[:] = np.nan
    train_plot[sequence_length:len(train_predict)+sequence_length] = train_predict.flatten()
    
    test_plot = np.empty_like(df['Close'].values)
    test_plot[:] = np.nan
    test_plot[len(train_predict)+sequence_length:len(train_predict)+len(test_predict)+sequence_length] = test_predict.flatten()
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Actual Price', color='blue')
    plt.plot(df.index, train_plot, label='Train Predictions', color='green')
    plt.plot(df.index, test_plot, label='Test Predictions', color='red')
    plt.title('Stock Price Prediction (AAPL)')
    plt.xlabel('Date')
    plt.ylabel('Close Price (USD)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/stock_price_prediction.png')
    plt.close()

def main():
    """Main function to run the stock price prediction."""
    # Load and preprocess data
    df = load_stock_data()
    sequence_length = 60
    X_train, X_test, y_train, y_test, scaler = preprocess_data(df, sequence_length)
    
    # Build and train model
    model = build_lstm_model(sequence_length)
    history = train_model(model, X_train, y_train)
    
    # Evaluate model
    train_predict, test_predict, train_r2, test_r2, train_trend_acc, test_trend_acc, train_loss, test_loss = evaluate_model(
        model, X_train, X_test, y_train, y_test, scaler, df
    )
    
    # Print results
    print("\nModel Performance Metrics:")
    print(f"Training Loss (MSE): {train_loss:.6f}")
    print(f"Test Loss (MSE): {test_loss:.6f}")
    print(f"Training R² Score: {train_r2:.4f}")
    print(f"Test R² Score: {test_r2:.4f}")
    print(f"Training Trend Accuracy: {train_trend_acc:.2f}%")
    print(f"Test Trend Accuracy: {test_trend_acc:.2f}%")
    
    # Plot results
    plot_results(df, train_predict, test_predict, sequence_length)
    print("\nPlot saved in 'plots' directory.")

if __name__ == '__main__':
    main()