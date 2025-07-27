import streamlit as st
from game_engine import GameEngine
from country_profiles import get_country_profiles
from utils import save_policy_draft, generate_press_release
import os

def main():
    """Main Streamlit app for AI policy debate simulation."""
    st.set_page_config(page_title="Global AI Policy Summit", layout="wide", initial_sidebar_state="expanded")
    
    # Initialize session state
    if 'game_engine' not in st.session_state:
        st.session_state.game_engine = GameEngine()
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "lobby"
    
    # Dark mode toggle
    with st.sidebar:
        st.header("Settings")
        if st.button("Toggle Dark Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
        if st.session_state.dark_mode:
            st.markdown("<style>body {background-color: #2c2f33; color: #ffffff;}</style>", unsafe_allow_html=True)
    
    # Navigation
    pages = {"Lobby": "lobby", "Debate Room": "debate", "Policy Draft": "policy", "Results": "results"}
    st.session_state.current_page = st.sidebar.radio("Navigate", list(pages.keys()), index=list(pages.values()).index(st.session_state.current_page))
    
    game = st.session_state.game_engine
    
    # Lobby Page
    if st.session_state.current_page == "lobby":
        st.title("🌍 Global AI Policy Summit")
        st.markdown("Role-play as a country delegate to negotiate AI policies. Choose your country and debate topic.")
        
        with st.form("lobby_form"):
            col1, col2 = st.columns(2)
            with col1:
                country = st.selectbox("Choose Your Country", list(get_country_profiles().keys()), index=0)
                anonymous = st.checkbox("Play Anonymously")
            with col2:
                topic = st.selectbox("Debate Topic", ["AI Surveillance Laws", "Military AI Limits", "Global AI Ethics", "Data Sharing", "Model Regulation"])
                mode = st.selectbox("Debate Mode", ["Turn-Based", "Free-Flow"])
            if st.form_submit_button("Start Summit"):
                game.setup_game(country, topic, mode, anonymous)
                st.session_state.current_page = "debate"
                st.experimental_rerun()
    
    # Debate Room
    elif st.session_state.current_page == "debate":
        st.title(f"🗣️ Debate Room: {game.topic}")
        game.run_debate()
    
    # Policy Draft Zone
    elif st.session_state.current_page == "policy":
        st.title("📑 Policy Draft Zone")
        game.run_policy_draft()
    
    # Results Page
    elif st.session_state.current_page == "results":
        st.title("📈 Summit Results")
        game.show_results()
        
        if st.button("Generate Press Release"):
            press_release = generate_press_release(game.results, game.topic)
            st.markdown(press_release)
        
        if st.button("Export Policy Draft"):
            pdf_file = save_policy_draft(game.policy_draft)
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="Download Policy PDF",
                    data=f.read(),
                    file_name="policy_draft.pdf",
                    mime="application/pdf"
                )

if __name__ == '__main__':
    main()