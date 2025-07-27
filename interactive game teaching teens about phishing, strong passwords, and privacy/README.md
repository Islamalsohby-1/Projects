CyberGuardians: Cybersecurity Game for Teens
A Python-based educational game for teenagers (ages 13–18) to learn about phishing detection, password strength, and digital privacy, built with Streamlit for a mobile-friendly interface.
Features

Three Game Modules:
Phishing Challenge: Identify phishing vs. legitimate emails with GPT-generated variations.
Password Strength Game: Create and test passwords using zxcvbn library.
Privacy Quiz: Make privacy-focused choices in social media and browsing scenarios.


Gamification: Real-time feedback, scoring, progress bars, and hints with emojis.
Streamlit Dashboard: 
Home page with module selection.
Interactive pages for each game.
Scoreboard, progress tracking, and downloadable PDF summary.


Optional Features:
Randomized phishing emails via GPT-4.
Dark mode toggle.
Local leaderboard for session-based tracking.
Teacher view for monitoring student scores.
Audio tips for accessibility (requires phishing_tip.mp3, password_tip.mp3, privacy_tip.mp3).
Modular design for adding new topics (e.g., 2FA, cookies).



Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save main.py, games/, utils/, assets/, and requirements.txt.
Set OpenAI API Key (for phishing email variations):
Set environment variable: export OPENAI_API_KEY='your-api-key' (Linux/Mac) or set OPENAI_API_KEY='your-api-key' (Windows).
Or add to .env file: OPENAI_API_KEY=your-api-key.


Install Dependencies:
Run: pip install -r requirements.txt


Add Assets:
Create assets/ folder.
Add sample email screenshots: phishing_email1.jpg, phishing_email2.jpg.
Add audio files: phishing_tip.mp3, password_tip.mp3, privacy_tip.mp3 (or create dummy MP3s for testing).


Run the Game:
Start Streamlit: streamlit run main.py
Open the URL (usually http://localhost:8501) on a browser or mobile device.


Gameplay:
Select a module (Phishing, Passwords, Privacy).
Answer questions, create passwords, or make choices.
View scores, feedback, and download session summary as PDF.


Teacher Usage:
Enable "Teacher View" to see all player scores.
Leaderboard saved in leaderboard.json.



Example Inputs

Phishing Challenge:
Sample email: "Subject: Urgent Account Verification\nDear User, your account will be suspended unless you verify your details at [link]."
Image: assets/phishing_email1.jpg (screenshot of a suspicious email).


Password Strength Game:
Input: "password123" → Feedback: "Weak, try adding symbols and length."


Privacy Quiz:
Scenario: "You get a friend request from someone you don’t know. What should you do?"
Correct Answer: "Ignore it."



Screenshots

Home Page: Module selection with welcome message and emojis.
Phishing Challenge: Email text and screenshot with Yes/No radio buttons.
Password Game: Password input with strength meter and suggestions.
Privacy Quiz: Scenario-based questions with multiple-choice options.
Scoreboard: Progress bars and feedback for all modules.

Notes

Runs in ~1 minute setup on a standard CPU.
Mobile-friendly with responsive Streamlit UI.
Requires internet for GPT-4 (phishing variations); other features work offline.
Audio files are optional; game functions without them.
Leaderboard and session data saved locally (leaderboard.json).
Modular structure allows adding new modules in games/ folder.
