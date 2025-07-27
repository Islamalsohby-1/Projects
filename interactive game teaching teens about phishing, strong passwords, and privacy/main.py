import streamlit as st
from games.phishing import PhishingChallenge
from games.passwords import PasswordStrengthGame
from games.privacy import PrivacyQuiz
from utils.scoring import ScoreManager
from utils.assets import load_email_images
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def save_session_summary(score_manager, filename="session_summary.pdf"):
    """Save session summary to PDF."""
    os.makedirs("outputs", exist_ok=True)
    c = canvas.Canvas(f"outputs/{filename}", pagesize=letter)
    c.drawString(100, 750, "Cybersecurity Game Summary")
    y = 730
    for module, data in score_manager.scores.items():
        c.drawString(100, y, f"{module}: {data['score']}/{data['total']}")
        y -= 20
        for feedback in data['feedback']:
            c.drawString(120, y, feedback[:80])
            y -= 20
            if y < 50:
                c.showPage()
                y = 750
    c.save()

def main():
    """Main Streamlit app for the cybersecurity game."""
    st.set_page_config(page_title="CyberGuardians", layout="wide")
    
    # Initialize session state
    if 'score_manager' not in st.session_state:
        st.session_state.score_manager = ScoreManager()
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Dark mode toggle
    with st.sidebar:
        st.header("Settings")
        if st.button("Toggle Dark Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
        if st.session_state.dark_mode:
            st.markdown("<style>body {background-color: #2c2f33; color: #ffffff;}</style>", unsafe_allow_html=True)
    
    # Welcome page
    st.title("🛡️ CyberGuardians: Learn Cybersecurity!")
    st.markdown("""
    Welcome, CyberGuardians! Test your skills in spotting phishing emails, creating strong passwords, and protecting your digital privacy.
    Choose a module below to start your mission! 🚀
    """)
    
    # Module selection
    module = st.selectbox("Choose a Game Module", ["Phishing Challenge", "Password Strength Game", "Privacy Quiz"])
    
    score_manager = st.session_state.score_manager
    
    # Initialize games
    phishing_game = PhishingChallenge()
    password_game = PasswordStrengthGame()
    privacy_game = PrivacyQuiz()
    
    # Render selected module
    if module == "Phishing Challenge":
        st.header("🐟 Phishing Challenge")
        phishing_game.run()
    elif module == "Password Strength Game":
        st.header("🔐 Password Strength Game")
        password_game.run()
    else:
        st.header("🕵️ Privacy Quiz")
        privacy_game.run()
    
    # Scoreboard and progress
    st.header("Scoreboard")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your Progress")
        for mod, data in score_manager.scores.items():
            score = data['score']
            total = data['total']
            st.progress(score / total if total > 0 else 0)
            st.write(f"{mod}: {score}/{total}")
    with col2:
        st.subheader("Feedback")
        for mod, data in score_manager.scores.items():
            for feedback in data['feedback'][-3:]:
                st.write(f"- {feedback}")
    
    # Download summary
    if st.button("Download Session Summary"):
        save_session_summary(score_manager)
        with open("outputs/session_summary.pdf", "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f.read(),
                file_name="session_summary.pdf",
                mime="application/pdf"
            )
    
    # Teacher view
    if st.checkbox("Teacher View"):
        st.header("Teacher Dashboard")
        for user, scores in score_manager.leaderboard.items():
            st.write(f"**{user}**:")
            for mod, data in scores.items():
                st.write(f"- {mod}: {data['score']}/{data['total']}")

if __name__ == '__main__':
    main()