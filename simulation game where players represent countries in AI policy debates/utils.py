from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openai import OpenAI
import os

def save_policy_draft(policy_text):
    """Save policy draft to PDF."""
    os.makedirs("outputs", exist_ok=True)
    pdf_file = "outputs/policy_draft.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.drawString(100, 750, "Global AI Policy Draft")
    y = 730
    for line in policy_text.split("\n"):
        if y < 50:
            c.showPage()
            y = 750
        c.drawString(100, y, line[:80])
        y -= 20
    c.save()
    return pdf_file

def generate_press_release(results, topic):
    """Generate a press release for the summit outcome."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""
    Write a concise press release (100-150 words) for a global AI policy summit on {topic}.
    Outcome: {results['policy']}.
    Voting: {', '.join([f'{c}: {v}' for c, v in results.get('votes', {}).items()])}.
    Highlight key agreements and tensions, referencing real-world AI events (e.g., EU AI Act).
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except:
        return f"Press Release: The Global AI Policy Summit on {topic} concluded with a draft policy."