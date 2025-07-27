Phishing Email Classifier
This project implements a machine learning model to classify emails as phishing or legitimate using text features.
Requirements

Python 3.8+
Install dependencies: pip install -r requirements.txt

How to Run

Ensure requirements.txt is in the same directory as phishing_classifier.py.
Run the script: python phishing_classifier.py
The script will:
Create a sample dataset (phishing_email_dataset.csv) if none exists
Train a Logistic Regression model
Save the model and vectorizer as phishing_model.pkl and tfidf_vectorizer.pkl
Print and save performance metrics to model_metrics.txt
Test a sample email
Start a CLI interface for real-time predictions


In the CLI, enter email subject and body to predict, or type 'quit' to exit.

Output Files

phishing_email_dataset.csv: Simulated dataset
phishing_model.pkl: Trained model
tfidf_vectorizer.pkl: TF-IDF vectorizer
model_metrics.txt: Performance metrics (accuracy, precision, recall, F1-score, confusion matrix)

Notes

The dataset is small and simulated for demonstration. Replace `phishing_email_dataset acompañado por un archivo CSV real de Kaggle/UCI para mejores resultados.
Precision target is 88%+, but actual performance depends on dataset quality.
The CLI interface allows testing new emails interactively.
