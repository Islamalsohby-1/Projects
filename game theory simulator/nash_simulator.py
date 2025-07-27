import numpy as np
import pandas as pd
from scipy.optimize import linprog
import plotly.graph_objects as go

def find_pure_nash_equilibria(payoff_player1, payoff_player2):
    """Find pure strategy Nash equilibria by checking mutual best responses."""
    nash_equilibria = []
    rows, cols = payoff_player1.shape
    
    for i in range(rows):
        for j in range(cols):
            player1_best = payoff_player1[i, j] == np.max(payoff_player1[:, j])
            player2_best = payoff_player2[i, j] == np.max(payoff_player2[i, :])
            if player1_best and player2_best:
                nash_equilibria.append((i, j))
    
    return nash_equilibria

def find_mixed_nash_equilibria(payoff_player1, payoff_player2):
    """Find mixed strategy Nash equilibria for 2x2 or 3x3 games using linear programming."""
    rows, cols = payoff_player1.shape
    if rows != cols or rows > 3:
        return None, None, "Mixed strategy calculation supported only for 2x2 or 3x3 games."
    
    # Player 1's mixed strategy
    c = np.ones(rows)  # Minimize sum of probabilities
    A_ub = -payoff_player2.T  # Negative payoffs for Player 2
    b_ub = np.zeros(cols)  # Ensure expected payoffs are equal
    A_eq = np.ones((1, rows))  # Probabilities sum to 1
    b_eq = [1]
    bounds = [(0, 1)] * rows
    
    result1 = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
    
    # Player 2's mixed strategy
    c = np.ones(cols)
    A_ub = -payoff_player1
    b_ub = np.zeros(rows)
    A_eq = np.ones((1, cols))
    result2 = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
    
    if result1.success and result2.success:
        p, q = result1.x, result2.x
        if all(0 <= pi <= 1 for pi in p) and all(0 <= qi <= 1 for qi in q):
            # Calculate expected payoffs
            exp_payoff1 = np.dot(p, np.dot(payoff_player1, q))
            exp_payoff2 = np.dot(p, np.dot(payoff_player2, q))
            return p, q, f"Mixed strategy equilibrium found. Expected payoffs: ({exp_payoff1:.2f}, {exp_payoff2:.2f})"
    
    return None, None, "No valid mixed strategy equilibrium found."

def find_dominant_strategies(payoff_player1, payoff_player2):
    """Identify dominant strategies for each player."""
    rows, cols = payoff_player1.shape
    dominant_strategies = {'Player 1': None, 'Player 2': None}
    
    # Player 1: Check row dominance
    for i in range(rows):
        is_dominant = True
        for j in range(cols):
            if not all(payoff_player1[i, j] >= payoff_player1[k, j] for k in range(rows) if k != i):
                is_dominant = False
                break
        if is_dominant:
            dominant_strategies['Player 1'] = f"Row {i+1}"
            break
    
    # Player 2: Check column dominance
    for j in range(cols):
        is_dominant = True
        for i in range(rows):
            if not all(payoff_player2[i, j] >= payoff_player2[i, k] for k in range(cols) if k != j):
                is_dominant = False
                break
        if is_dominant:
            dominant_strategies['Player 2'] = f"Column {j+1}"
            break
    
    return dominant_strategies

def is_pareto_optimal(payoff_player1, payoff_player2, i, j):
    """Check if outcome (i, j) is Pareto optimal."""
    rows, cols = payoff_player1.shape
    for m in range(rows):
        for n in range(cols):
            if (payoff_player1[m, n] > payoff_player1[i, j] and payoff_player2[m, n] >= payoff_player2[i, j]) or \
               (payoff_player1[m, n] >= payoff_player1[i, j] and payoff_player2[m, n] > payoff_player2[i, j]):
                return False
    return True

def analyze_equilibria(payoff_player1, payoff_player2, row_labels, col_labels):
    """Analyze game: equilibria, dominant strategies, and Pareto optimality."""
    pure_nash = find_pure_nash_equilibria(payoff_player1, payoff_player2)
    mixed_nash_p, mixed_nash_q, mixed_message = find_mixed_nash_equilibria(payoff_player1, payoff_player2)
    dominant_strategies = find_dominant_strategies(payoff_player1, payoff_player2)
    
    analysis = []
    analysis.append("**Pure Strategy Nash Equilibria**:")
    if pure_nash:
        for i, j in pure_nash:
            pareto_status = "Pareto optimal" if is_pareto_optimal(payoff_player1, payoff_player2, i, j) else "Not Pareto optimal"
            stability = "Stable" if len(pure_nash) == 1 or (mixed_nash_p is None) else "Potentially unstable due to multiple equilibria"
            analysis.append(f" - Outcome ({row_labels[i]}, {col_labels[j]}): Payoffs ({payoff_player1[i, j]}, {payoff_player2[i, j]}), {pareto_status}, {stability}")
    else:
        analysis.append(" - None found.")
    
    analysis.append("\n**Mixed Strategy Nash Equilibrium**:")
    if mixed_nash_p is not None:
        p_str = ", ".join([f"{row_labels[i]}: {p:.2f}" for i, p in enumerate(mixed_nash_p)])
        q_str = ", ".join([f"{col_labels[j]}: {q:.2f}" for j, q in enumerate(mixed_nash_q)])
        analysis.append(f" - Player 1: {p_str}")
        analysis.append(f" - Player 2: {q_str}")
        analysis.append(f" - {mixed_message}")
    else:
        analysis.append(f" - {mixed_message}")
    
    analysis.append("\n**Dominant Strategies**:")
    for player, strategy in dominant_strategies.items():
        analysis.append(f" - {player}: {strategy if strategy else 'None'}")
    
    return "\n".join(analysis)

def plot_best_response(payoff_player1, payoff_player2, row_labels, col_labels):
    """Create best response plot for 2x2 games."""
    if payoff_player1.shape != (2, 2):
        return None
    p = np.linspace(0, 1, 100)
    # Player 1's best response
    br1 = []
    for p2 in p:
        exp_payoff_row1 = p2 * payoff_player1[0, 0] + (1 - p2) * payoff_player1[0, 1]
        exp_payoff_row2 = p2 * payoff_player1[1, 0] + (1 - p2) * payoff_player1[1, 1]
        br1.append(1 if exp_payoff_row1 > exp_payoff_row2 else 0 if exp_payoff_row1 < exp_payoff_row2 else 0.5)
    
    # Player 2's best response
    br2 = []
    for p1 in p:
        exp_payoff_col1 = p1 * payoff_player2[0, 0] + (1 - p1) * payoff_player2[1, 0]
        exp_payoff_col2 = p1 * payoff_player2[0, 1] + (1 - p1) * payoff_player2[1, 1]
        br2.append(1 if exp_payoff_col1 > exp_payoff_col2 else 0 if exp_payoff_col1 < exp_payoff_col2 else 0.5)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=p, y=br1, mode='lines', name="Player 1 Best Response", line=dict(color='blue')))
    fig.add_trace(go.Scatter(y=p, x=br2, mode='lines', name="Player 2 Best Response", line=dict(color='red')))
    fig.update_layout(
        title="Best Response Functions",
        xaxis_title="Player 2 Prob. (Column 1)",
        yaxis_title="Player 1 Prob. (Row 1)",
        showlegend=True,
        xaxis_range=[0, 1],
        yaxis_range=[0, 1],
        width=400,
        height=400
    )
    return fig