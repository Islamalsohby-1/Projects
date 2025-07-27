Enhanced News Article Summarizer
A stunning Python tool for summarizing news articles using the BART-large-CNN model from HuggingFace. Features a modern Tailwind CSS web interface, robust CLI, and coherence checking.
Installation

Clone or download this project.
Create a virtual environment (recommended):python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install -r requirements.txt



Usage
Command Line Interface (CLI)
Summarize a text file:
python summarizer.py --input news_article.txt

Summarize direct text:
python summarizer.py --text "Your article text here..."

Output appears in the console.
Web Interface
Start the Flask app:
python summarizer.py --web

Visit http://localhost:5000, paste an article, and click "Summarize" for a stunning UI experience.
Sample Files

news_article.txt: Sample input article.
sample_output.txt: Example summary output.

Notes

Requires Python 3.8+.
Internet connection needed for initial model downloads.
Coherence check uses cosine similarity (threshold: 0.8).
Web interface uses Tailwind CSS for a modern, responsive design.
Error handling ensures robust operation.
