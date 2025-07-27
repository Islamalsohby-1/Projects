from openai import OpenAI
import os
from market_data import get_market_insights
import uuid

class IdeaGenerator:
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_ideas(self, skills, interests, country, business_type, startup_stage, num_ideas, include_emerging_tech, tech_level, audience, industry):
        """Generate startup ideas based on user inputs."""
        market_insights = get_market_insights(country)
        prompt = f"""
        Generate {num_ideas} startup ideas for a user with:
        - Skills: {skills}
        - Interests: {interests}
        - Location: {country} ({market_insights})
        - Business Type: {business_type}
        - Startup Stage: {startup_stage}
        - Tech Level: {tech_level}
        - Target Audience: {', '.join(audience)}
        - Industry: {', '.join(industry)}
        {'Include emerging technologies (AI, Web3, IoT) in the ideas.' if include_emerging_tech else ''}
        For each idea, provide:
        - Title and one-line pitch
        - Problem solved
        - Target market and local relevance
        - MVP description
        - Monetization strategy
        - Competitive edge
        - First 3 validation steps
        - Tech stack/tools
        - Difficulty (1-5) and funding estimate
        - Category (e.g., EdTech, HealthTech)
        - Branding: Name + slogan
        - Landing page: Hero text + CTA
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.8
            )
            ideas_text = response.choices[0].message.content
            ideas = []
            for idea_block in ideas_text.split("\n\n"):
                idea = self.parse_idea(idea_block)
                if idea:
                    idea['id'] = str(uuid.uuid4())
                    ideas.append(idea)
            return ideas[:num_ideas]
        except Exception as e:
            st.error(f"Error generating ideas: {str(e)}")
            return []

    def parse_idea(self, idea_text):
        """Parse GPT output into structured idea format."""
        try:
            lines = idea_text.split("\n")
            idea = {}
            for line in lines:
                if line.startswith("Title:"):
                    idea['title'] = line.replace("Title:", "").strip()
                elif line.startswith("Pitch:"):
                    idea['pitch'] = line.replace("Pitch:", "").strip()
                elif line.startswith("Problem:"):
                    idea['problem'] = line.replace("Problem:", "").strip()
                elif line.startswith("Target Market:"):
                    idea['target_market'] = line.replace("Target Market:", "").strip()
                elif line.startswith("MVP:"):
                    idea['mvp'] = line.replace("MVP:", "").strip()
                elif line.startswith("Monetization:"):
                    idea['monetization'] = line.replace("Monetization:", "").strip()
                elif line.startswith("Competitive Edge:"):
                    idea['competitive_edge'] = line.replace("Competitive Edge:", "").strip()
                elif line.startswith("Validation Steps:"):
                    idea['validation_steps'] = [step.strip() for step in line.replace("Validation Steps:", "").split(";")]
                elif line.startswith("Tech Stack:"):
                    idea['tech_stack'] = line.replace("Tech Stack:", "").strip()
                elif line.startswith("Difficulty:"):
                    idea['difficulty'] = line.replace("Difficulty:", "").strip()
                elif line.startswith("Category:"):
                    idea['category'] = line.replace("Category:", "").strip()
                elif line.startswith("Branding:"):
                    idea['branding'] = line.replace("Branding:", "").strip()
                elif line.startswith("Landing Page:"):
                    idea['landing_page'] = line.replace("Landing Page:", "").strip()
            return idea if idea.get('title') else None
        except:
            return None

    def refine_idea(self, idea):
        """Refine a specific idea with additional details."""
        prompt = f"Refine this startup idea with more details and improvements:\n{format_idea_to_markdown(idea)}"
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            return self.parse_idea(response.choices[0].message.content) or idea
        except:
            return idea

    def get_investor_feedback(self, idea):
        """Simulate investor feedback on an idea."""
        prompt = f"Provide constructive investor feedback for this startup idea:\n{format_idea_to_markdown(idea)}"
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except:
            return "Unable to generate investor feedback."

    def generate_slide_deck(self, idea):
        """Generate a text-based slide deck preview for an idea."""
        prompt = f"Create a concise slide deck preview (text only) for this startup idea:\n{format_idea_to_markdown(idea)}"
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except:
            return "Unable to generate slide deck preview."