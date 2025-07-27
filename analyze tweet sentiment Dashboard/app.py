import pandas as pd
import nltk
import re
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from flask import Flask, request, render_template
import os

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

app = Flask(__name__)

# Create or load a sample dataset
def create_sample_dataset():
    data = {
        'text': [
            "I love this movie, it's amazing! #happy",
            "Terrible service, very disappointed 😞",
            "Just okay, nothing special about it",
            "Wow, fantastic experience! Highly recommend",
            "Worst day ever, everything went wrong",
            "Pretty good, could be better though",
            "This is so cool! #awesome",
            "Not impressed, quite boring",
            "Absolutely wonderful time!",
            "Really bad product, waste of money"
        ],
        'sentiment': [
            'positive',
            'negative',
            'neutral',
            'positive',
            'negative',
            'neutral',
            'positive',
            'negative',
            'positive',
            'negative'
        ]
    }
    df = pd.DataFrame(data)
    df.to_csv('sample_tweets.csv', index=False)
    return df

# Preprocessing function
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove mentions and hashtags
    text = re.sub(r'@\w+|#\w+', '', text)
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(tokens)

# Train the model
def train_model(df):
    # Preprocess all tweets
    df['cleaned_text'] = df['text'].apply(preprocess_text)
    
    # Create feature vectors
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(df['cleaned_text'])
    y = df['sentiment']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Naive Bayes classifier
    classifier = MultinomialNB()
    classifier.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = classifier.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return classifier, vectorizer, accuracy

# Load or create dataset and train model
if not os.path.exists('sample_tweets.csv'):
    df = create_sample_dataset()
else:
    df = pd.read_csv('sample_tweets.csv')

classifier, vectorizer, model_accuracy = train_model(df)

# Flask routes
@app.route('/')
def home():
    return render_template('index.html', accuracy=model_accuracy)

@app.route('/predict', methods=['POST'])
def predict():
    tweet = request.form['tweet']
    cleaned_tweet = preprocess_text(tweet)
    features = vectorizer.transform([cleaned_tweet])
    prediction = classifier.predict(features)[0]
    return render_template('index.html', prediction=prediction, tweet=tweet, accuracy=model_accuracy)

@app.route('/test')
def test():
    sample_tweets = df['text'].head(10).tolist()
    predictions = []
    for tweet in sample_tweets:
        cleaned_tweet = preprocess_text(tweet)
        features = vectorizer.transform([cleaned_tweet])
        prediction = classifier.predict(features)[0]
        predictions.append((tweet, prediction))
    return render_template('test.html', predictions=predictions, accuracy=model_accuracy)

if __name__ == '__main__':
    app.run(debug=True)