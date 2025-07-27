import os
import json
from ocr_utils import extract_text_from_image, extract_text_from_pdf
from gpt_utils import generate_gpt_summary, generate_flashcards
from PIL import Image
import cv2
import numpy as np
import layoutparser as lp
from datetime import datetime

class NoteProcessor:
    def __init__(self):
        """Initialize the note processor with history storage."""
        self.history_file = 'processing_history.json'
        self.history = self.load_history()
        self.ocr_model = 'tesseract'  # Default OCR model
        self.model = lp.Detectron2LayoutModel(
            config_path='lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
            label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
        )

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

    def process_file(self, file_path, ocr_model='tesseract', gpt_format='summary', prompt_style='default', focus_region=None):
        """Process an image or PDF file to extract and summarize content."""
        try:
            # Extract text based on file type
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
                'file_path': file_path,
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

if __name__ == '__main__':
    processor = NoteProcessor()
    raw_text, summary, flashcards, layout = processor.process_file(
        'sample_input.jpg', gpt_format='summary', prompt_style='default'
    )
    print("Raw OCR Text:", raw_text)
    print("\nSummary:", summary)
    if flashcards:
        print("\nFlashcards:", flashcards)
    processor.save_output(summary, 'md', 'sample_output.md')