Global AI Policy Summit
A Streamlit-based simulation game where players role-play as country delegates negotiating AI policies on topics like safety, surveillance, and ethics.
Features

Role-Playing: Choose a country (USA, China, EU, India) with unique goals, stance, and constraints.
Debate Topics: AI surveillance, military AI, global ethics, data sharing, model regulation.
Gameplay:
Turn-based or free-flow debate modes.
GPT-4-powered NPC delegates with realistic responses.
Policy drafting and voting.
Scoring for diplomacy, alliances, trust.


Streamlit Dashboard:
Lobby: Select country, topic, mode.
Debate Room: Interactive discussion with sentiment analysis.
Policy Draft Zone: Propose and vote on resolutions.
Results: Show outcomes, alliances, and exportable PDF.


Optional Features:
Surprise events (e.g., AI accidents).
Real-time translation simulation (via GPT).
Gamified leaderboard.
Anonymous mode.
AI-generated press release.
Dark/light mode.
References to real-world AI events (EU AI Act, Bletchley Declaration).



Setup Instructions

Install Python: Ensure Python 3.8+ (https://www.python.org/downloads/).
Clone or Create Files: Save main_app.py, game_engine.py, gpt_npc.py, country_profiles.py, policy_topics.py, utils.py, requirements.txt.
Set OpenAI API Key:
Set environment variable: export OPENAI_API_KEY='your-api-key' (Linux/Mac) or set OPENAI_API_KEY='your-api-key' (Windows).
Or add to .env: OPENAI_API_KEY=your-api-key.


Install Dependencies:
Run: pip install -r requirements.txt


Run the App:
Start Streamlit: streamlit run main_app.py
Open URL (usually http://localhost:8501).


Gameplay:
Lobby: Choose country, topic, mode.
Debate: Submit statements, see NPC responses.
Draft: Propose policy, vote.
Results: View outcomes, export PDF, generate press release.



Test Inputs

Country: EU
Topic: Global AI Ethics
Mode: Turn-Based
Statement: "We propose a global AI ethics framework based on the EU AI Act, prioritizing transparency."

Example Output
Policy Draft: Framework for ethical AI development, inspired by EU AI Act.Votes: EU: Approve, USA: Abstain, China: Reject, India: ApproveScores: Diplomacy: 6/10, Alliances: 4/10, Trust: 5/10Press Release: The Global AI Policy Summit concluded with a proposed ethical AI framework, inspired by the EU AI Act. The EU and India approved, while China rejected, citing national priorities.
Notes

Runs in ~1-2 minutes on standard CPU.
Requires internet for GPT-4.
Policy drafts saved in outputs/policy_draft.pdf.
Modular design for adding new topics or countries.
Assets folder can include icons/maps (optional).
