Note to Summary Converter
A Python tool that converts handwritten notes or diagrams (from images or PDFs) into structured summaries using OCR and GPT-4, with a Streamlit dashboard.
Features

OCR: Extracts text from images (JPG/PNG) or PDFs using Tesseract/pytesseract.
Image Preprocessing: Grayscale, denoising, and thresholding for better OCR accuracy.
Diagram Interpretation: Uses layoutparser to identify text, titles, lists, tables, and figures.
GPT-4 Summarization: Cleans, rephrases, and summarizes extracted text into summary, outline, teaching, or Q&A formats.
Flashcards: Generates Q&A flashcards from content when selected.
Streamlit UI: Upload files, edit OCR output, choose output format, download results, and view history.
Output Formats: Save as .txt, .md, or .pdf.
Customization: Prompt styles (default, teaching_12yo, technical) and focus region highlighting.
History: Saves last 100 processing entries for reuse.

Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Install Tesseract: Download and install Tesseract OCR (https://github.com/tesseract-ocr/tesseract).
Install Poppler: Required for PDF processing (https://poppler.freedesktop.org/).
Clone or Create Files: Save ocr_to_summary.py, streamlit_app.py, gpt_utils.py, ocr_utils.py, requirements.txt.
Set OpenAI API Key:
Set environment variable: export OPENAI_API_KEY='your-api-key'
Or add to .env file: OPENAI_API_KEY=your-api-key


`

System: It looks like your request for a Python tool that converts handwritten or diagram-based notes into structured summaries was cut off during the generation of the README.md file. Since you asked for a complete, ready-to-run project with all files and no explanations, I’ll provide the complete set of files, ensuring the README.md is fully populated and includes all necessary details. I’ll also include a sample input image and an example GPT summary as requested, maintaining the modular, production-ready structure.
Below is the complete project, including all files (ocr_to_summary.py, streamlit_app.py, gpt_utils.py, ocr_utils.py, requirements.txt, README.md, a sample input image, and an example output summary). The code is designed to run in under 5 minutes on a standard CPU, handles both images and PDFs, uses Tesseract for OCR, integrates GPT-4 for summarization, and includes all optional features (diagram interpretation, flashcard generation, prompt customization, history saving, and error handling).


import os
import json
from ocr_utils import extract_text_from_image, extract_text_from_pdf
from gpt_utils import generate_gpt_summary, generate_flashcards
from PIL import Image
import cv2
import numpy as np
import layoutparser as lp
from datetime import datetime

class NoteProcessor:    def init(self):        """Initialize the note processor with history storage."""        self.history_file = 'processing_history.json'        self.history = self.load_history()        self.ocr_model = 'tesseract'  # Default OCR model        self.model = lp.Detectron2LayoutModel(            config_path='lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',            label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]        )
def load_history(self):
    """Load processing history from file."""
    if os.path.exists(self.history_file):
        with open(self.history_file, 'r') as f:
            return json.load(f)
    return []

def save_history(self, entry):
    """Save processing history to file."""
    self.history.append(entry)
    with open(self.history_file, 'w') as f:
        json.dump(self.history[-100:], f, indent=2)

def process_file(self, file_path, ocr_model='tesseract', gpt_format='summary', prompt_style='default', focus_region=None, raw_text=None):
    """Process an image or PDF file to extract and summarize content."""
    try:
        # Use provided raw text or extract from file
        layout = None
        if raw_text is None:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                raw_text, layout = extract_text_from_image(file_path, ocr_model, focus_region)
            elif file_path.lower().endswith('.pdf'):
                raw_text, layout = extract_text_from_pdf(file_path, ocr_model, focus_region)
            else:
                raise ValueError("Unsupported file format")

        # Generate GPT summary
        summary = generate_gpt_summary(raw_text, gpt_format, prompt_style, layout)

        # Generate flashcards if requested
        flashcards = generate_flashcards(raw_text) if gpt_format == 'qa' else []

        # Save to history
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'file_path': file_path if file_path else 'manual_input',
            'ocr_model': ocr_model,
            'gpt_format': gpt_format,
            'prompt_style': prompt_style,
            'raw_text': raw_text,
            'summary': summary,
            'flashcards': flashcards
        }
        self.save_history(entry)

        return raw_text, summary, flashcards, layout

    except Exception as e:
        return f"Error processing file: {str(e)}", "", [], None

def save_output(self, summary, output_format, filename):
    """Save the processed output to a file."""
    os.makedirs('outputs', exist_ok=True)
    output_path = os.path.join('outputs', filename)
    
    if output_format == 'txt':
        with open(output_path, 'w') as f:
            f.write(summary)
    elif output_format == 'md':
        with open(output_path, 'w') as f:
            f.write(f"# Summary\n\n{summary}")
    elif output_format == 'pdf':
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(output_path, pagesize=letter)
        c.drawString(100, 750, "Summary")
        y = 730
        for line in summary.split('\n'):
            if y < 50:
                c.showPage()
                y = 750
            c.drawString(100, y, line[:100])
            y -= 20
        c.save()

if name == 'main':    processor = NoteProcessor()    raw_text, summary, flashcards, layout = processor.process_file(        'sample_input.jpg', gpt_format='summary', prompt_style='default'    )    print("Raw OCR Text:", raw_text)    print("\nSummary:", summary)    if flashcards:        print("\nFlashcards:", flashcards)    processor.save_output(summary, 'md', 'sample_output.md')