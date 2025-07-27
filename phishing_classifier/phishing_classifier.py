# Phishing Email Classifier
# Uses a simulated dataset and Logistic Regression for binary classification
# Features: subject, body, label (0=legit, 1=phishing)

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import joblib
import os

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# 1. Simulate a phishing email dataset
def create_sample_dataset():
    data = {
        'subject': [
            'Your account has been compromised', 'Meeting tomorrow at 10', 'Win a free iPhone', 
            'Invoice payment due', 'Security alert: Update your password', 'Lunch plans?', 
            'Claim your prize now', 'Project deadline reminder', 'Urgent: Verify your bank details', 
            'Team outing this Friday'
        ],
        'body': [
            'Dear user, your account was accessed from an unknown device. Click here to secure it.',
            'Hi team, let’s discuss the project tomorrow at 10 AM. Regards, John.',
            'Congratulations! You’ve won a free iPhone. Click to claim your prize now!',
            'Please find the attached invoice. Payment is due by Friday.',
            'Your password is weak. Update it now to avoid account suspension.',
            'Hey, want to grab lunch today? Let me know!',
            'You’re our lucky winner! Provide your details to claim your prize.',
            'Don’t forget the project deadline is next week. Stay on track!',
            'Your bank account needs verification. Click here to avoid suspension.',
            'Looking forward to the team outing. RSVP by Wednesday!'
        ],
        'label': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    }
    df = pd.DataFrame(data)
    df.to_csv('phishing_email_dataset.csv', index=False)
    return df

# 2. Text preprocessing
def preprocess_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# 3. Predict new email
def predict_email(subject, body, vectorizer, model):
    # Combine subject and body
    text = subject + ' ' + body
    # Preprocess
    text = preprocess_text(text)
    # Transform using the same vectorizer
    text_vector = vectorizer.transform([text])
    # Predict
    prediction = model.predict(text_vector)
    return 'Phishing' if prediction[0] == 1 else 'Legitimate'

# 4. Main function
def main():
    # Load or create dataset
    if not os.path.exists('phishing_email_dataset.csv'):
        df = create_sample_dataset()
    else:
        df = pd.read_csv('phishing_email_dataset.csv')
    
    # Combine subject and body for feature extraction
    df['text'] = df['subject'] + ' ' + df['body']
    # Preprocess text
    df['text'] = df['text'].apply(preprocess_text)
    
    # Feature extraction with TfidfVectorizer
    vectorizer = TfidfVectorizer(max_features=500)
    X = vectorizer.fit_transform(df['text'])
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Logistic Regression model
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    metrics = {
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred),
        'Recall': recall_score(y_test, y_pred),
        'F1 Score': f1_score(y_test, y_pred)
    }
    cm = confusion_matrix(y_test, y_pred)
    
    # Print metrics
    print("Model Performance Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    print("\nConfusion Matrix:")
    print(cm)
    
    # Save model and vectorizer
    joblib.dump(model, 'phishing_model.pkl')
    joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
    
    # Save metrics to file
    with open('model_metrics.txt', 'w') as f:
        f.write("Model Performance Metrics:\n")
        for metric, value in metrics.items():
            f.write(f"{metric}: {value:.4f}\n")
        f.write("\nConfusion Matrix:\n")
        f.write(str(cm))
    
    # Test a new email
    test_subject = "Urgent: Account Verification Required"
    test_body = "Your account needs immediate verification. Click here to proceed."
    result = predict_email(test_subject, test_body, vectorizer, model)
    print(f"\nTest Email Prediction: {result}")

# 5. CLI interface for real-time prediction
def cli_interface():
    model = joblib.load('phishing_model.pkl')
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    print("\nPhishing Email Classifier CLI")
    print("Enter 'quit' to exit")
    while True:
        subject = input("\nEnter email subject: ")
        if subject.lower() == 'quit':
            break
        body = input("Enter email body: ")
        if body.lower() == 'quit':
            break
        result = predict_email(subject, body, vectorizer, model)
        print(f"Prediction: {result}")

if __name__ == "__main__":
    main()
    cli_interface()