Nash Equilibrium Simulator
A Python application to simulate and analyze Nash equilibria in 2-player strategic games using Streamlit.
Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save nash_simulator.py, game_data.py, app.py, and requirements.txt.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the App:
Run: streamlit run app.py
Open the provided URL (usually http://localhost:8501) in a browser.


Usage:
Select a predefined game (Prisoner's Dilemma, Battle of the Sexes, Matching Pennies) or enter a custom 2x2 payoff matrix.
View the payoff matrix with Nash equilibria highlighted and read the strategic analysis.
Expand the "Understanding the Analysis" section for explanations of key concepts.



Notes

Runs in ~5 minutes with a standard Python setup.
Uses Streamlit for the UI, numpy/pandas for calculations, and plotly for matrix visualization.
Predefined games are stored in game_data.py; add new games by editing this file with the same structure.
