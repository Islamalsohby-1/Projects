import streamlit as st
from utils.scoring import ScoreManager
from utils.questions import get_phishing_questions
from utils.assets import load_email_images
from openai import OpenAI
import random

class PhishingChallenge:
    def __init__(self):
        """Initialize phishing challenge with questions and images."""
        self.questions = get_phishing_questions()
        self.images = load_email_images()
        self.client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
        self.score_manager = st.session_state.score_manager
        self.current_question = None

    def generate_phishing_variant(self, base_text):
        """Generate a variant of a phishing email using GPT."""
        try:
            prompt = f"Rewrite this phishing email with slight variations but keep it deceptive:\n{base_text}"
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            return response.choices[0].message.content
        except:
            return base_text

    def run(self):
        """Run the phishing challenge game."""
        if 'phishing_index' not in st.session_state:
            st.session_state.phishing_index = 0
            st.session_state.phishing_answers = []
        
        if st.session_state.phishing_index >= len(self.questions):
            st.success("Challenge Complete!")
            return
        
        question = self.questions[st.session_state.phishing_index]
        if random.random() > 0.5:
            question['text'] = self.generate_phishing_variant(question['text'])
        
        st.markdown(f"**Question {st.session_state.phishing_index + 1}**")
        if question['image']:
            st.image(f"assets/{question['image']}", caption="Email Screenshot", width=300)
        st.write(question['text'])
        
        answer = st.radio("Is this a phishing email?", ["Yes", "No"], key=f"phishing_{st.session_state.phishing_index}")
        if st.button("Submit Answer"):
            is_correct = (answer == "Yes" and question['is_phishing']) or (answer == "No" and not question['is_phishing'])
            feedback = f"{'Correct!' if is_correct else 'Incorrect.'} {question['explanation']}"
            self.score_manager.add_score("Phishing Challenge", 1 if is_correct else 0, 1, feedback)
            st.session_state.phishing_answers.append({
                "question": question['text'],
                "answer": answer,
                "correct": is_correct,
                "explanation": question['explanation']
            })
            st.session_state.phishing_index += 1
            st.experimental_rerun()
        
        # Audio tip
        if st.button("🔊 Audio Hint"):
            st.audio("assets/phishing_tip.mp3")