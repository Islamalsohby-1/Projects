# app.py
# A sophisticated Flask-based negotiation simulator with advanced tactics, analytics, and web interface

import random
import json
import os
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
from io import StringIO

# --- Negotiation Classes ---

class Negotiator:
    """Represents a negotiator with advanced tactics and dynamic behavior."""
    def __init__(self, name, role, initial_offer, reservation_price, target_price, batna, tactic="moderate"):
        self.name = name
        self.role = role  # Buyer or Seller
        self.initial_offer = initial_offer
        self.reservation_price = reservation_price
        self.target_price = target_price
        self.batna = batna
        self.tactic = tactic  # anchor_high, moderate, hold_firm, collaborative, competitive
        self.current_offer = initial_offer
        self.previous_offers = []
        self.concession_rate = 0.0  # Tracks average concession per round
        self.bluff_factor = random.uniform(0.0, 0.2) if tactic == "competitive" else 0.0

    def make_offer(self, round_num, opponent_offer=None, opponent_history=None):
        """Generate an offer based on tactic, round, and opponent behavior."""
        if round_num == 1 and self.tactic == "anchor_high":
            offer = self._anchor_offer()
        elif self.tactic == "hold_firm":
            offer = self.current_offer
            if opponent_offer:
                concession = self._calculate_concession(opponent_offer, factor=0.1)
                offer = self._adjust_offer(concession)
        elif self.tactic == "collaborative":
            offer = self._collaborative_offer(opponent_offer, opponent_history)
        elif self.tactic == "competitive":
            offer = self._competitive_offer(opponent_offer)
        else:  # moderate
            offer = self._moderate_offer(opponent_offer)

        # Apply bluffing for competitive tactic
        if self.tactic == "competitive" and random.random() < self.bluff_factor:
            offer = self._apply_bluff(offer)

        self.previous_offers.append(offer)
        self.current_offer = offer
        if len(self.previous_offers) > 1:
            self.concession_rate = abs(self.previous_offers[-1] - self.previous_offers[-2]) / max(1, len(self.previous_offers) - 1)
        return offer

    def _anchor_offer(self):
        """Generate an extreme initial offer for anchoring."""
        if self.role == "Buyer":
            return max(self.initial_offer - 1500, self.batna - 500)
        else:
            return min(self.initial_offer + 1500, self.reservation_price + 500)

    def _moderate_offer(self, opponent_offer):
        """Generate a moderate offer with balanced concessions."""
        if opponent_offer:
            concession = self._calculate_concession(opponent_offer, factor=0.5)
            return self._adjust_offer(concession)
        return self.current_offer

    def _collaborative_offer(self, opponent_offer, opponent_history):
        """Generate an offer aiming for mutual benefit."""
        if opponent_offer and opponent_history:
            avg_opponent_concession = sum(abs(opponent_history[i] - opponent_history[i-1]) 
                                         for i in range(1, len(opponent_history))) / max(1, len(opponent_history) - 1)
            concession = self._calculate_concession(opponent_offer, factor=min(0.7, avg_opponent_concession / 1000))
            return self._adjust_offer(concession)
        return self.current_offer

    def _competitive_offer(self, opponent_offer):
        """Generate an aggressive offer with minimal concessions."""
        if opponent_offer:
            concession = self._calculate_concession(opponent_offer, factor=0.2)
            return self._adjust_offer(concession)
        return self.current_offer

    def _apply_bluff(self, offer):
        """Apply a random bluff to the offer."""
        if self.role == "Buyer":
            return offer * (1 - self.bluff_factor)
        else:
            return offer * (1 + self.bluff_factor)

    def _calculate_concession(self, opponent_offer, factor=0.5):
        """Calculate concession based on opponent's offer."""
        if self.role == "Buyer":
            if opponent_offer <= self.reservation_price:
                return (opponent_offer - self.current_offer) * factor
            return 0
        else:
            if opponent_offer >= self.reservation_price:
                return (opponent_offer - self.current_offer) * factor
            return 0

    def _adjust_offer(self, concession):
        """Adjust offer within reservation price bounds."""
        if self.role == "Buyer":
            new_offer = self.current_offer + concession
            return min(new_offer, self.reservation_price)
        else:
            new_offer = self.current_offer + concession
            return max(new_offer, self.reservation_price)

    def accept_offer(self, opponent_offer):
        """Decide whether to accept an offer."""
        if self.role == "Buyer":
            return opponent_offer <= self.reservation_price
        else:
            return opponent_offer >= self.reservation_price

    def evaluate_batna(self, final_offer):
        """Evaluate if final offer is better than BATNA."""
        if self.role == "Buyer":
            return final_offer <= self.batna
        else:
            return final_offer >= self.batna

class NegotiationEngine:
    """Manages the negotiation process and analytics."""
    def __init__(self, negotiator1, negotiator2, max_rounds=6):
        self.negotiator1 = negotiator1
        self.negotiator2 = negotiator2
        self.max_rounds = max_rounds
        self.history = []
        self.agreed_value = None
        self.start_time = datetime.now()

    def run_negotiation(self):
        """Simulate negotiation and return outcome."""
        for round_num in range(1, self.max_rounds + 1):
            offer1 = self.negotiator1.make_offer(round_num, self.negotiator2.current_offer, self.negotiator2.previous_offers)
            self.history.append((self.negotiator1.name, offer1, "offered"))
            
            if self.negotiator2.accept_offer(offer1):
                self.agreed_value = offer1
                self.history.append((self.negotiator2.name, offer1, "accepted"))
                break

            offer2 = self.negotiator2.make_offer(round_num, offer1, self.negotiator1.previous_offers)
            self.history.append((self.negotiator2.name, offer2, "offered"))
            
            if self.negotiator1.accept_offer(offer2):
                self.agreed_value = offer2
                self.history.append((self.negotiator1.name, offer2, "accepted"))
                break

        return self._analyze_outcome()

    def _analyze_outcome(self):
        """Analyze negotiation outcome with detailed metrics."""
        duration = (datetime.now() - self.start_time).total_seconds()
        outcome = {
            "agreement_reached": self.agreed_value is not None,
            "final_value": self.agreed_value,
            "winner": None,
            "batna_comparison": {},
            "tactics_summary": {
                self.negotiator1.name: {
                    "tactic": self.negotiator1.tactic,
                    "offers": self.negotiator1.previous_offers,
                    "concession_rate": self.negotiator1.concession_rate
                },
                self.negotiator2.name: {
                    "tactic": self.negotiator2.tactic,
                    "offers": self.negotiator2.previous_offers,
                    "concession_rate": self.negotiator2.concession_rate
                }
            },
            "duration_seconds": duration,
            "rounds": len(self.negotiator1.previous_offers),
            "history": self.history
        }

        if self.agreed_value:
            n1_diff = abs(self.agreed_value - self.negotiator1.target_price)
            n2_diff = abs(self.agreed_value - self.negotiator2.target_price)
            outcome["winner"] = (self.negotiator1.name if n1_diff < n2_diff else
                               self.negotiator2.name if n2_diff < n1_diff else "Tie")
            outcome["batna_comparison"][self.negotiator1.name] = (
                "Better than BATNA" if self.negotiator1.evaluate_batna(self.agreed_value) else "Worse than BATNA"
            )
            outcome["batna_comparison"][self.negotiator2.name] = (
                "Better than BATNA" if self.negotiator2.evaluate_batna(self.agreed_value) else "Worse than BATNA"
            )
        else:
            outcome["winner"] = "No agreement"
            outcome["batna_comparison"][self.negotiator1.name] = f"Fell back to BATNA: ${self.negotiator1.batna:.2f}"
            outcome["batna_comparison"][self.negotiator2.name] = f"Fell back to BATNA: ${self.negotiator2.batna:.2f}"

        return outcome

# --- Flask App ---

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    """Render the main negotiation interface."""
    return render_template('index.html')

@app.route('/start_negotiation', methods=['POST'])
def start_negotiation():
    """Handle negotiation simulation based on user input."""
    try:
        data = request.form
        name = data.get('name', 'User')
        role = data.get('role', 'Buyer')
        if role not in ['Buyer', 'Seller']:
            return jsonify({'error': 'Invalid role. Choose Buyer or Seller.'}), 400

        initial_offer = float(data.get('initial_offer', 0))
        reservation_price = float(data.get('reservation_price', 0))
        target_price = float(data.get('target_price', 0))
        batna = float(data.get('batna', 0))
        tactic = data.get('tactic', 'moderate')
        if tactic not in ['anchor_high', 'moderate', 'hold_firm', 'collaborative', 'competitive']:
            return jsonify({'error': 'Invalid tactic.'}), 400

        user = Negotiator(name, role, initial_offer, reservation_price, target_price, batna, tactic)
        
        ai_role = 'Seller' if role == 'Buyer' else 'Buyer'
        ai_initial = initial_offer + random.uniform(-1500, 1500)
        ai_reservation = reservation_price + random.uniform(-1000, 1000)
        ai_target = target_price + random.uniform(-800, 800)
        ai_batna = batna + random.uniform(-500, 500)
        ai_tactic = random.choice(['anchor_high', 'moderate', 'hold_firm', 'collaborative', 'competitive'])
        ai = Negotiator('AI', ai_role, ai_initial, ai_reservation, ai_target, ai_batna, ai_tactic)

        engine = NegotiationEngine(user, ai)
        outcome = engine.run_negotiation()

        return jsonify(outcome)
    except ValueError:
        return jsonify({'error': 'Invalid numeric input.'}), 400

@app.route('/run_test_case/<int:case_id>')
def run_test_case(case_id):
    """Run a predefined test case."""
    test_cases = [
        {
            "name": "Test Case 1: Moderate vs Collaborative",
            "negotiator1": Negotiator("Alice", "Buyer", 5000, 7000, 6000, 7500, "moderate"),
            "negotiator2": Negotiator("Bob", "Seller", 9000, 7000, 8000, 6500, "collaborative")
        },
        {
            "name": "Test Case 2: Anchor-High vs Competitive",
            "negotiator1": Negotiator("Charlie", "Buyer", 4000, 6500, 5500, 7000, "anchor_high"),
            "negotiator2": Negotiator("Dana", "Seller", 8500, 6000, 7500, 5500, "competitive")
        },
        {
            "name": "Test Case 3: Hold-Firm vs Moderate",
            "negotiator1": Negotiator("Eve", "Buyer", 4500, 6800, 5700, 7200, "hold_firm"),
            "negotiator2": Negotiator("Frank", "Seller", 8800, 6500, 7800, 6000, "moderate")
        }
    ]

    if 0 <= case_id < len(test_cases):
        case = test_cases[case_id]
        engine = NegotiationEngine(case["negotiator1"], case["negotiator2"])
        outcome = engine.run_negotiation()
        outcome["test_case_name"] = case["name"]
        return jsonify(outcome)
    return jsonify({'error': 'Invalid test case ID.'}), 400

@app.route('/download_summary', methods=['POST'])
def download_summary():
    """Download negotiation outcome as JSON."""
    outcome = request.json
    filename = f"negotiation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with StringIO() as sio:
        json.dump(outcome, sio, indent=2)
        sio.seek(0)
        return send_file(
            sio,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )

# --- Main Execution ---

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)