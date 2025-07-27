Conflict Resolution Simulator
A Flask-based web app to simulate conflict resolution scenarios in workplace, family, team, or school settings.
Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save app.py, scenarios.json, requirements.txt, and create a templates/ folder with index.html.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the App:
Run: python app.py
Open a browser and go to http://127.0.0.1:5000


Usage:
Select a scenario, make choices, and see feedback/outcomes.
Use "Start Over" or "Try Another Scenario" to explore more.
Reflect on outcomes in the provided text box.



Adding New Scenarios

Edit scenarios.json to add new scenarios.
Follow the existing structure: id, title, background, characters, conflicting_goals, and nested steps with description, options, feedback, next, and optional outcome/reflection.
Ensure unique id values and valid JSON format.

Notes

Runs in ~5 minutes with a standard Python setup.
Mobile-friendly UI with simple CSS.
Uses Flask for lightweight web serving.
