# Enhanced Python summarization tool using HuggingFace Transformers and Flask
# Requirements: Python 3.8+, pip install -r requirements.txt
# CLI Usage: python summarizer.py --input news_article.txt or --text "Your article text"
# Flask Usage: python summarizer.py --web (visit http://localhost:5000)
# Sample input: news_article.txt
# Sample output: Printed to console or displayed in web form

import argparse
import re
import torch
from transformers import BartForConditionalGeneration, BartTokenizer
from flask import Flask, request, render_template_string
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download NLTK data
try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    logging.error(f"Failed to download NLTK data: {e}")
    sys.exit(1)

# Initialize model and tokenizer
MODEL_NAME = "facebook/bart-large-cnn"
try:
    tokenizer = BartTokenizer.from_pretrained(MODEL_NAME)
    model = BartForConditionalGeneration.from_pretrained(MODEL_NAME)
except Exception as e:
    logging.error(f"Failed to load model or tokenizer: {e}")
    sys.exit(1)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
logging.info(f"Using device: {device}")

# Initialize sentence transformer for coherence check
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    logging.error(f"Failed to load sentence transformer: {e}")
    sys.exit(1)

# Clean and preprocess text
def preprocess_text(text):
    try:
        if not text or len(text.strip()) < 50:
            raise ValueError("Input text is too short or empty")
        text = re.sub(r'\s+', ' ', text.strip())  # Normalize whitespace
        text = re.sub(r'\n+', ' ', text)  # Replace newlines
        sentences = sent_tokenize(text)
        if not sentences:
            raise ValueError("No valid sentences detected")
        return ' '.join(sentences[:100])[:4000]  # Limit input size
    except Exception as e:
        logging.error(f"Text preprocessing failed: {e}")
        raise

# Generate summary
def generate_summary(text, min_length=30, max_length=150):
    try:
        inputs = tokenizer(preprocess_text(text), max_length=1024, truncation=True, return_tensors="pt").to(device)
        summary_ids = model.generate(
            inputs['input_ids'],
            max_length=max_length,
            min_length=min_length,
            length_penalty=1.0,
            num_beams=6,
            early_stopping=True,
            no_repeat_ngram_size=3
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    except Exception as e:
        logging.error(f"Summary generation failed: {e}")
        raise

# Check coherence using cosine similarity
def check_coherence(original, summary):
    try:
        embeddings = embedder.encode([original[:1000], summary])
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return score >= 0.8
    except Exception as e:
        logging.warning(f"Coherence check failed: {e}")
        return False

# CLI function
def cli_summarize(input_source, is_file=True):
    try:
        if is_file:
            with open(input_source, 'r', encoding='utf-8') as f:
                article = f.read()
        else:
            article = input_source
        summary = generate_summary(article)
        coherence = check_coherence(article, summary)
        print("\nSummary:")
        print(summary)
        print(f"\nCoherence check passed: {coherence}")
    except Exception as e:
        logging.error(f"CLI summarization failed: {e}")
        print(f"Error: {e}")

# Flask app
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Summarizer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: linear-gradient(to bottom right, #1e3a8a, #3b82f6); }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-2xl">
        <h1 class="text-3xl font-bold text-center text-gray-800 mb-6">News Article Summarizer</h1>
        <form method="POST" class="space-y-4">
            <textarea name="article" class="w-full h-64 p-4 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500" placeholder="Paste your news article here..." required></textarea>
            <button type="submit" class="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition duration-200">Summarize</button>
        </form>
        {% if summary %}
        <div class="mt-6 p-4 bg-gray-100 rounded-lg">
            <h3 class="text-xl font-semibold text-gray-800">Summary:</h3>
            <p class="text-gray-700 mt-2">{{ summary }}</p>
            <p class="text-sm text-gray-500 mt-2">Coherence check passed: {{ coherence }}</p>
        </div>
        {% endif %}
        {% if error %}
        <div class="mt-6 p-4 bg-red-100 rounded-lg text-red-700">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    coherence = None
    error = None
    if request.method == 'POST':
        article = request.form.get('article')
        try:
            if article:
                summary = generate_summary(article)
                coherence = check_coherence(article, summary)
            else:
                error = "Please provide a valid article."
        except Exception as e:
            error = f"Error processing article: {str(e)}"
    return render_template_string(HTML_TEMPLATE, summary=summary, coherence=coherence, error=error)

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced News Article Summarizer")
    parser.add_argument('--input', type=str, help="Path to input text file")
    parser.add_argument('--text', type=str, help="Direct text input for summarization")
    parser.add_argument('--web', action='store_true', help="Run Flask web server")
    args = parser.parse_args()

    try:
        if args.web:
            app.run(debug=False, host='0.0.0.0', port=5000)
        elif args.input:
            cli_summarize(args.input, is_file=True)
        elif args.text:
            cli_summarize(args.text, is_file=False)
        else:
            print("Please provide --input <file>, --text <string>, or --web flag")
    except Exception as e:
        logging.error(f"Application failed: {e}")
        print(f"Error: {e}")