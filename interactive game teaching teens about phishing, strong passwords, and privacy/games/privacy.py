import streamlit as st
from utils.scoring import ScoreManager
from utils.questions import get_privacy_questions

class PrivacyQuiz:
    def __init__(self):
        """Initialize privacy quiz with questions."""
        self.questions = get_privacy_questions()
        self.score_manager = st.session_state.score_manager

    def run(self):
        """Run the privacy quiz game."""
        if 'privacy_index' not in st.session_state:
            st.session_state.privacy_index = 0
            st.session_state.privacy_answers = []
        
        if st.session_state.privacy_index >= len(self.questions):
            st.success("Quiz Complete!")
            return
        
        question = self.questions[st.session_state.privacy_index]
        st.markdown(f"**Question {st.session_state.privacy_index + 1}**")
        st.write(question['scenario'])
        
        answer = st.radio("Choose the best option:", question['options'], key=f"privacy_{st.session_state.privacy_index}")
        if st.button("Submit Answer"):
            is_correct = answer == question['correct_answer']
            feedback = f"{'Correct!' if is_correct else 'Incorrect.'} {question['explanation']}"
            self.score_manager.add_score("Privacy Quiz", 1 if is_correct else 0, 1, feedback)
            st.session_state.privacy_answers.append({
                "scenario": question['scenario'],
                "answer": answer,
                "correct": is_correct,
                "explanation": question['explanation']
            })
            st.session_state.privacy_index += 1
            st.experimental_rerun()
        
        # Audio tip
        if st.button("🔊 Audio Hint"):
            st.audio("assets/privacy_tip.mp3")