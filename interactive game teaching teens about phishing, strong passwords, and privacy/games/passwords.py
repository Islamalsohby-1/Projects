import streamlit as st
from zxcvbn import zxcvbn
from utils.scoring import ScoreManager

class PasswordStrengthGame:
    def __init__(self):
        """Initialize password strength game."""
        self.score_manager = st.session_state.score_manager
        self.levels = [
            {"min_score": 0, "hint": "Try a mix of letters, numbers, and symbols."},
            {"min_score": 2, "hint": "Make it longer and avoid common words."},
            {"min_score": 4, "hint": "Great! Add unique characters for max strength."}
        ]

    def run(self):
        """Run the password strength game."""
        st.markdown("**Create a Strong Password**")
        password = st.text_input("Enter a password:", type="password", key="password_input")
        
        if password:
            result = zxcvbn(password)
            score = result['score']
            feedback = result['feedback']['suggestions']
            strength = ["Very Weak", "Weak", "Fair", "Good", "Strong"][score]
            
            st.write(f"Password Strength: **{strength}** (Score: {score}/4)")
            st.progress(score / 4)
            
            if feedback:
                st.write("Suggestions:")
                for f in feedback:
                    st.write(f"- {f}")
            
            for level in self.levels:
                if score >= level['min_score']:
                    st.write(f"Hint: {level['hint']}")
            
            if st.button("Submit Password"):
                self.score_manager.add_score("Password Strength Game", score, 4, f"Password scored {score}/4: {feedback}")
                st.success("Password submitted!")
        
        # Audio tip
        if st.button("🔊 Audio Hint"):
            st.audio("assets/password_tip.mp3")