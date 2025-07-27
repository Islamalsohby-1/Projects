import streamlit as st
from idea_engine import IdeaGenerator
from utils import save_ideas, load_ideas, format_idea_to_markdown, generate_pdf
import os

def main():
    """Streamlit app for startup idea generation."""
    st.set_page_config(page_title="Startup Idea Generator", layout="wide")
    
    # Initialize session state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'ideas' not in st.session_state:
        st.session_state.ideas = []
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    
    # Dark mode toggle
    with st.sidebar:
        st.header("Settings")
        if st.button("Toggle Dark Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
        if st.session_state.dark_mode:
            st.markdown("<style>body {background-color: #2c2f33; color: #ffffff;}</style>", unsafe_allow_html=True)
        
        # Filters
        st.header("Filters")
        tech_level = st.selectbox("Tech Level", ["Low", "Medium", "High"], index=1)
        audience = st.multiselect("Target Audience", ["B2C", "B2B", "Enterprise", "Non-profit"], default=["B2C"])
        industry = st.multiselect("Industry", ["EdTech", "HealthTech", "AgriTech", "FinTech", "SaaS", "E-commerce"], default=["SaaS"])
    
    # Main UI
    st.title("🚀 Startup Idea Generator")
    st.markdown("Enter your details to generate personalized startup ideas based on your skills, interests, and local market needs.")
    
    # Input form
    with st.form("idea_form"):
        col1, col2 = st.columns(2)
        with col1:
            skills = st.text_area("Your Skills (e.g., Python, marketing, design)", "Python, UI/UX design")
            interests = st.text_area("Your Interests/Passions (e.g., healthcare, education)", "Sustainability, education")
            country = st.text_input("Country/Region (e.g., Kenya, India)", "Kenya")
        with col2:
            business_type = st.selectbox("Business Type", ["Tech", "Service", "Product", "SaaS"], index=3)
            startup_stage = st.selectbox("Startup Stage", ["Idea", "MVP", "Scaling"], index=0)
            num_ideas = st.select_slider("Number of Ideas", options=[1, 5, 10], value=5)
            include_emerging_tech = st.checkbox("Include Emerging Tech (AI, Web3, IoT)", value=True)
        submitted = st.form_submit_button("Generate Ideas")
    
    if submitted:
        generator = IdeaGenerator()
        st.session_state.ideas = generator.generate_ideas(
            skills=skills,
            interests=interests,
            country=country,
            business_type=business_type,
            startup_stage=startup_stage,
            num_ideas=num_ideas,
            include_emerging_tech=include_emerging_tech,
            tech_level=tech_level,
            audience=audience,
            industry=industry
        )
        save_ideas(st.session_state.ideas)
    
    # Display ideas
    if st.session_state.ideas:
        st.header("Generated Startup Ideas")
        for i, idea in enumerate(st.session_state.ideas):
            with st.expander(f"{idea['title']} - {idea['pitch']}"):
                st.markdown(format_idea_to_markdown(idea))
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Favorite", key=f"fav_{i}"):
                        if idea not in st.session_state.favorites:
                            st.session_state.favorites.append(idea)
                with col2:
                    if st.button("Refine Idea", key=f"refine_{i}"):
                        refined_idea = IdeaGenerator().refine_idea(idea)
                        st.session_state.ideas[i] = refined_idea
                        save_ideas(st.session_state.ideas)
                        st.experimental_rerun()
                with col3:
                    if st.button("Investor Feedback", key=f"feedback_{i}"):
                        feedback = IdeaGenerator().get_investor_feedback(idea)
                        st.write(f"**Investor Feedback**: {feedback}")
    
    # Favorites
    if st.session_state.favorites:
        st.header("Favorite Ideas")
        for idea in st.session_state.favorites:
            st.write(f"- {idea['title']}: {idea['pitch']}")
    
    # Export options
    if st.session_state.ideas:
        st.header("Export Ideas")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Export as Markdown"):
                md_content = "\n\n".join([format_idea_to_markdown(idea) for idea in st.session_state.ideas])
                with open("outputs/ideas.md", "w") as f:
                    f.write(md_content)
                st.download_button(
                    label="Download Markdown",
                    data=md_content,
                    file_name="ideas.md",
                    mime="text/markdown"
                )
        with col2:
            if st.button("Export as PDF"):
                pdf_file = generate_pdf(st.session_state.ideas)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f.read(),
                        file_name="ideas.pdf",
                        mime="application/pdf"
                    )
        with col3:
            if st.button("Generate Slide Deck Preview"):
                deck = IdeaGenerator().generate_slide_deck(st.session_state.ideas[0])
                st.markdown(deck)
    
    # History
    st.header("Session History")
    history = load_ideas()
    for entry in history[-5:]:
        st.write(f"[{entry['timestamp']}] {entry['title']}: {entry['pitch']}")

if __name__ == '__main__':
    main()