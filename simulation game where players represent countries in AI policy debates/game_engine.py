from gpt_npc import NPCDelegate
from country_profiles import get_country_profiles
from policy_topics import get_topic_details
import streamlit as st
import random

class GameEngine:
    def __init__(self):
        """Initialize game engine."""
        self.country = None
        self.topic = None
        self.mode = None
        self.anonymous = False
        self.delegates = {}
        self.turn = 0
        self.scores = {"diplomacy": 0, "alliances": 0, "trust": 0}
        self.policy_draft = ""
        self.results = {}
        self.sentiment_history = []
        self.surprise_triggered = False

    def setup_game(self, country, topic, mode, anonymous):
        """Set up the game with selected country, topic, and mode."""
        self.country = country
        self.topic = topic
        self.mode = mode
        self.anonymous = anonymous
        self.delegates = {c: NPCDelegate(c, topic) for c in get_country_profiles().keys() if c != country}
        self.delegates[country] = None  # Player-controlled
        self.scores = {"diplomacy": 0, "alliances": 0, "trust": 0}
        self.policy_draft = ""
        self.results = {}
        self.turn = 0
        self.sentiment_history = []
        self.surprise_triggered = False

    def run_debate(self):
        """Run the debate phase."""
        st.markdown(f"**Country**: {self.country if not self.anonymous else 'Anonymous Delegate'}")
        st.markdown(f"**Topic**: {self.topic}")
        
        # Display country profiles in sidebar
        with st.sidebar:
            st.header("Country Profiles")
            for country, delegate in self.delegates.items():
                if country == self.country:
                    continue
                st.subheader(country)
                st.write(f"Stance: {get_country_profiles()[country]['stance']}")
                st.write(f"Goals: {get_country_profiles()[country]['goals']}")
        
        # Surprise event
        if random.random() < 0.2 and not self.surprise_triggered:
            surprise = f"🚨 Breaking News: AI incident reported in {random.choice(list(self.delegates.keys()))}! Details impact {self.topic.lower()}."
            st.warning(surprise)
            self.surprise_triggered = True
            self.sentiment_history.append(("Surprise", surprise))

        if self.mode == "Turn-Based":
            self.run_turn_based()
        else:
            self.run_free_flow()

    def run_turn_based(self):
        """Run turn-based debate."""
        if 'debate_turns' not in st.session_state:
            st.session_state.debate_turns = []
        
        st.markdown(f"**Turn {self.turn + 1}**")
        player_input = st.text_area("Your Statement:", key=f"turn_{self.turn}")
        if st.button("Submit Statement"):
            if player_input:
                sentiment = self.analyze_sentiment(player_input)
                self.sentiment_history.append((self.country, sentiment))
                st.session_state.debate_turns.append((self.country, player_input))
                
                # NPC responses
                for country, delegate in self.delegates.items():
                    if country != self.country:
                        response = delegate.respond(player_input, self.topic)
                        st.session_state.debate_turns.append((country, response))
                        self.sentiment_history.append((country, self.analyze_sentiment(response)))
                
                self.turn += 1
                self.update_scores()
                if self.turn >= 3:
                    st.session_state.current_page = "policy"
                    st.experimental_rerun()
        
        # Display debate history
        for speaker, statement in st.session_state.debate_turns[-5:]:
            st.markdown(f"**{speaker if not (speaker == self.country and self.anonymous) else 'Anonymous'}:** {statement}")

    def run_free_flow(self):
        """Run free-flow debate."""
        player_input = st.text_area("Your Statement:", key="free_flow")
        if st.button("Submit Statement"):
            if player_input:
                sentiment = self.analyze_sentiment(player_input)
                self.sentiment_history.append((self.country, sentiment))
                st.write(f"**{self.country if not self.anonymous else 'Anonymous'}:** {player_input}")
                
                # NPC responses
                for country, delegate in self.delegates.items():
                    if country != self.country:
                        response = delegate.respond(player_input, self.topic)
                        st.write(f"**{country}:** {response}")
                        self.sentiment_history.append((country, self.analyze_sentiment(response)))
                
                self.update_scores()
                if len(self.sentiment_history) >= 10:
                    st.session_state.current_page = "policy"
                    st.experimental_rerun()

    def run_policy_draft(self):
        """Run policy draft phase."""
        st.markdown("Propose and vote on a policy resolution.")
        with st.form("policy_form"):
            self.policy_draft = st.text_area("Draft Policy:", value=self.policy_draft or get_topic_details(self.topic)['template'])
            if st.form_submit_button("Submit for Vote"):
                votes = {country: random.choice(["Approve", "Reject", "Abstain"]) for country in self.delegates}
                votes[self.country] = "Approve"
                st.write("**Vote Results**:")
                for country, vote in votes.items():
                    st.write(f"{country}: {vote}")
                self.results = {"policy": self.policy_draft, "votes": votes}
                st.session_state.current_page = "results"
                st.experimental_rerun()

    def show_results(self):
        """Show summit results."""
        st.markdown("**Final Policy**:")
        st.write(self.policy_draft)
        st.markdown("**Voting Outcome**:")
        for country, vote in self.results.get("votes", {}).items():
            st.write(f"{country}: {vote}")
        
        st.markdown("**Scores**:")
        st.write(f"- Diplomacy: {self.scores['diplomacy']}/10")
        st.write(f"- Alliances: {self.scores['alliances']}/10")
        st.write(f"- Trust: {self.scores['trust']}/10")
        
        st.markdown("**Sentiment Analysis**:")
        for speaker, sentiment in self.sentiment_history[-5:]:
            st.write(f"{speaker}: {sentiment}")

    def analyze_sentiment(self, text):
        """Placeholder for sentiment analysis."""
        return random.choice(["Positive", "Neutral", "Negative"])

    def update_scores(self):
        """Update scores based on sentiment and interactions."""
        positive_count = sum(1 for _, s in self.sentiment_history if s == "Positive")
        self.scores["diplomacy"] = min(10, positive_count * 2)
        self.scores["alliances"] = min(10, len(self.sentiment_history) // 2)
        self.scores["trust"] = min(10, positive_count)