from openai import OpenAI
from country_profiles import get_country_profiles
import os

class NPCDelegate:
    def __init__(self, country, topic):
        """Initialize NPC delegate with country and topic."""
        self.country = country
        self.topic = topic
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.profile = get_country_profiles()[country]

    def respond(self, player_statement, topic):
        """Generate NPC response using GPT-4."""
        prompt = f"""
        You are a delegate from {self.country} in a global AI policy summit discussing {topic}.
        Your country’s stance: {self.profile['stance']}.
        Your goals: {self.profile['goals']}.
        Your constraints: {self.profile['constraints']}.
        Respond to this statement: "{player_statement}".
        Use diplomatic language reflecting {self.country}'s cultural tone and policy alignment.
        Reference real-world AI events (e.g., EU AI Act, Bletchley Declaration) if relevant.
        Keep response concise (50-100 words).
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"{self.country} delegate: We appreciate your input and will consider it."