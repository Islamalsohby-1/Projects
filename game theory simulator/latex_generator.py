def generate_latex_report(game_name, description, payoff_player1, payoff_player2, row_labels, col_labels, analysis):
    """Generate LaTeX code for a game analysis report."""
    rows, cols = payoff_player1.shape
    matrix_content = "\\\\\n".join([
        " & ".join([f"({payoff_player1[i, j]:.1f}, {payoff_player2[i, j]:.1f})" for j in range(cols)])
        for i in range(rows)
    ])
    
    latex = r"""
\documentclass[a4paper,12pt]{article}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage[utf8]{inputenc}
\usepackage{noto}

\begin{document}

\begin{center}
    \textbf{\Large Nash Equilibrium Analysis: """ + game_name.replace("_", r"\ ") + r"""}
\end{center}

\section*{Game Description}
""" + description + r"""

\section*{Payoff Matrix}
\begin{table}[h]
\centering
\begin{tabular}{c|""" + "c" * cols + r"""}
\toprule
 & """ + " & ".join(col_labels) + r""" \\
\midrule
""" + " \\\\\n".join([f"{row_labels[i]} & {matrix_content.split('\\\\\n')[i]}" for i in range(rows)]) + r""" \\
\bottomrule
\end{tabular}
\caption{Payoff Matrix (Player 1, Player 2)}
\end{table}

\section*{Strategic Analysis}
\begin{verbatim}
""" + analysis.replace("_", r"\ ") + r"""
\end{verbatim}

\section*{Key Concepts}
\begin{itemize}
    \item \textbf{Nash Equilibrium}: A strategy pair where neither player can improve their payoff by unilaterally changing their strategy.
    \item \textbf{Dominant Strategy}: A strategy that is optimal regardless of the opponent's actions.
    \item \textbf{Pareto Optimality}: An outcome where no player can be better off without making another worse off.
    \item \textbf{Stability}: Equilibria are stable if unique or supported by dominant strategies.
\end{itemize}

\end{document}
"""
    return latex.encode('utf-8')