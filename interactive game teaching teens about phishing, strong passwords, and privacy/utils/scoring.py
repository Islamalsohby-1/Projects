import os
import json

class ScoreManager:
    def __init__(self):
        """Initialize score manager with local storage."""
        self.scores = {
            "Phishing Challenge": {"score": 0, "total": 0, "feedback": []},
            "Password Strength Game": {"score": 0, "total": 0, "feedback": []},
            "Privacy Quiz": {"score": 0, "total": 0, "feedback": []}
        }
        self.leaderboard = {}
        self.user_id = "Player1"  # Default user ID
        self.load_leaderboard()

    def add_score(self, module, score, total, feedback):
        """Add score and feedback for a module."""
        self.scores[module]["score"] += score
        self.scores[module]["total"] += total
        self.scores[module]["feedback"].append(feedback)
        self.leaderboard[self.user_id] = self.scores
        self.save_leaderboard()

    def set_user(self, user_id):
        """Set user ID for leaderboard."""
        self.user_id = user_id
        if user_id not in self.leaderboard:
            self.leaderboard[user_id] = {
                "Phishing Challenge": {"score": 0, "total": 0, "feedback": []},
                "Password Strength Game": {"score": 0, "total": 0, "feedback": []},
                "Privacy Quiz": {"score": 0, "total": 0, "feedback": []}
            }

    def load_leaderboard(self):
        """Load leaderboard from file."""
        if os.path.exists("leaderboard.json"):
            with open("leaderboard.json", "r") as f:
                self.leaderboard = json.load(f)

    def save_leaderboard(self):
        """Save leaderboard to file."""
        with open("leaderboard.json", "w") as f:
            json.dump(self.leaderboard, f, indent=2)