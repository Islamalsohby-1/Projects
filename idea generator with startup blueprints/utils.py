import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def format_idea_to_markdown(idea):
    """Format an idea into markdown text."""
    return f"""
## {idea['title']}
**Pitch**: {idea['pitch']}

**Problem**: {idea['problem']}

**Target Market**: {idea['target_market']}

**MVP**: {idea['mvp']}

**Monetization**: {idea['monetization']}

**Competitive Edge**: {idea['competitive_edge']}

**Validation Steps**:
- {idea['validation_steps'][0]}
- {idea['validation_steps'][1]}
- {idea['validation_steps'][2]}

**Tech Stack**: {idea['tech_stack']}

**Difficulty**: {idea['difficulty']}

**Category**: {idea['category']}

**Branding**: {idea['branding']}

**Landing Page**: {idea['landing_page']}
"""

def save_ideas(ideas):
    """Save ideas to a JSON file."""
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/ideas_history.json", "w") as f:
        json.dump(ideas, f, indent=2)

def load_ideas():
    """Load ideas from history file."""
    if os.path.exists("outputs/ideas_history.json"):
        with open("outputs/ideas_history.json", "r") as f:
            return json.load(f)
    return []

def generate_pdf(ideas):
    """Generate a PDF from ideas."""
    pdf_file = "outputs/ideas.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    y = 750
    for idea in ideas:
        c.drawString(100, y, idea['title'])
        y -= 20
        c.drawString(120, y, f"Pitch: {idea['pitch']}")
        y -= 20
        c.drawString(120, y, f"Problem: {idea['problem'][:80]}")
        y -= 20
        if y < 100:
            c.showPage()
            y = 750
    c.save()
    return pdf_file