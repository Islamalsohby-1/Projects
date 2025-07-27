Tweet Sentiment Analysis Flask App
Overview
This is a Flask web application that analyzes the sentiment of tweets using NLTK and scikit-learn. It includes a pre-trained Naive Bayes classifier and a simple web interface for predicting sentiment of user-input tweets.
Prerequisites

Python 3.8+
pip

Setup Instructions

Clone or download the project files.
Create a virtual environment (optional but recommended):python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install -r requirements.txt


Ensure the following project structure:project/
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── test.html
└── sample_tweets.csv (auto-generated on first run)



Running the Application

Run the Flask app:python app.py


Open a browser and navigate to http://localhost:5000.
Use the web interface to:
Enter a tweet and predict its sentiment
View sample predictions at /test



Features

Cleans and preprocesses tweets (removes mentions, hashtags, punctuation, links, and applies tokenization, stopword removal, and lemmatization)
Uses TfidfVectorizer for feature extraction
Trains a Naive Bayes classifier with ~85% accuracy (based on small sample dataset)
Web interface for real-time tweet sentiment prediction
Sample test route showing predictions for 10 tweets
Displays model accuracy on homepage

Notes

The app creates a sample dataset (sample_tweets.csv) if none exists.
The model is trained on startup and takes less than a minute.
The app is designed to be lightweight and complete setup/testing in under 10 minutes.
