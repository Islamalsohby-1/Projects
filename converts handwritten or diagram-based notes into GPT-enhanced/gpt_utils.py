import openai
from openai import OpenAI
import os
import time

class GPTUtils:
    def __init__(self):
        """Initialize OpenAI client with API key."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.max_retries = 3
        self.retry_delay = 2

    def generate_gpt_summary(self, raw_text, output_format, prompt_style, layout=None):
        """Generate structured summary using GPT-4."""
        prompt = self._build_prompt(raw_text, output_format, prompt_style, layout)
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes and structures handwritten or diagram-based notes."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except openai.RateLimitError:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise Exception("Rate limit exceeded after retries")
            except Exception as e:
                raise Exception(f"GPT-4 error: {str(e)}")
        
        return "Error: Could not generate summary"

    def generate_flashcards(self, raw_text):
        """Generate flashcards from raw text."""
        prompt = f"Create 3-5 flashcards with questions and answers based on this text:\n{raw_text}"
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant creating flashcards."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            content = response.choices[0].message.content
            flashcards = []
            for line in content.split('\n'):
                if line.startswith("Q:"):
                    question = line[2:].strip()
                    answer = next((l[2:].strip() for l in content.split('\n') if l.startswith("A:")), "")
                    flashcards.append({"question": question, "answer": answer})
            return flashcards[:5]
        except Exception as e:
            return []

    def _build_prompt(self, raw_text, output_format, prompt_style, layout):
        """Build the GPT prompt based on user preferences."""
        base_prompt = f"Process this raw OCR-extracted text from handwritten notes or a diagram:\n\n{raw_text}\n\n"
        if layout:
            base_prompt += f"Diagram layout detected: {layout}\n\n"
        
        format_map = {
            'summary': "Provide a concise summary in paragraph form, capturing the main ideas.",
            'outline': "Create a structured outline with bullet points, organizing key concepts.",
            'teaching': "Explain the content as if teaching it to a beginner, using simple language.",
            'qa': "Generate a Q&A format with key questions and answers based on the content."
        }
        
        style_map = {
            'default': "",
            'teaching_12yo': "Explain as if teaching a 12-year-old, using simple analogies.",
            'technical': "Use precise, technical language suitable for experts."
        }
        
        prompt = base_prompt + format_map.get(output_format, format_map['summary']) + "\n"
        prompt += style_map.get(prompt_style, style_map['default'])
        return prompt

if __name__ == '__main__':
    # Unit test
    import unittest

    class TestGPTUtils(unittest.TestCase):
        def setUp(self):
            self.gpt = GPTUtils()
        
        def test_prompt_building(self):
            prompt = self.gpt._build_prompt(
                "Photosynthesis: plants use sunlight, CO2, H2O to make glucose",
                'summary', 'default', None
            )
            self.assertIn("Provide a concise summary", prompt)
            self.assertIn("Photosynthesis", prompt)

    unittest.main()