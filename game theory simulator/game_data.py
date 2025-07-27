# Predefined game payoff matrices (2x2 and 3x3)
GAMES = {
    "Prisoner's Dilemma": {
        "description": "Two prisoners decide whether to confess or stay silent. Confessing is dominant, but mutual silence yields better outcomes.",
        "payoff_player1": [[-1, -3], [0, -2]],  # Row: Cooperate, Defect
        "payoff_player2": [[-1, 0], [-3, -2]],  # Column: Cooperate, Defect
        "row_labels": ["Cooperate", "Defect"],
        "col_labels": ["Cooperate", "Defect"]
    },
    "Battle of the Sexes": {
        "description": "A couple chooses between opera and football, preferring to be together but with different favorites.",
        "payoff_player1": [[2, 0], [0, 1]],  # Row: Opera, Football
        "payoff_player2": [[1, 0], [0, 2]],  # Column: Opera, Football
        "row_labels": ["Opera", "Football"],
        "col_labels": ["Opera", "Football"]
    },
    "Matching Pennies": {
        "description": "One player aims to match, the other to mismatch, choosing heads or tails.",
        "payoff_player1": [[1, -1], [-1, 1]],  # Row: Heads, Tails
        "payoff_player2": [[-1, 1], [1, -1]],  # Column: Heads, Tails
        "row_labels": ["Heads", "Tails"],
        "col_labels": ["Heads", "Tails"]
    },
    "Rock-Paper-Scissors": {
        "description": "Classic 3x3 game where each strategy beats one and loses to another.",
        "payoff_player1": [[0, -1, 1], [1, 0, -1], [-1, 1, 0]],  # Row: Rock, Paper, Scissors
        "payoff_player2": [[0, 1, -1], [-1, 0, 1], [1, -1, 0]],  # Column: Rock, Paper, Scissors
        "row_labels": ["Rock", "Paper", "Scissors"],
        "col_labels": ["Rock", "Paper", "Scissors"]
    }
}