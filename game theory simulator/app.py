import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from game_data import GAMES
from nash_simulator import find_pure_nash_equilibria, analyze_equilibria, plot_best_response
import latex_generator

def create_payoff_table(payoff_player1, payoff_player2, row_labels, col_labels, nash_equilibria):
    """Create an interactive Plotly table for payoff matrices."""
    rows, cols = payoff_player1.shape
    cell_colors = [['white' for _ in range(cols)] for _ in range(rows)]
    for i, j in nash_equilibria:
        cell_colors[i][j] = 'lightgreen'
    
    cell_text = [[f"({payoff_player1[i, j]:.1f}, {payoff_player2[i, j]:.1f})" for j in range(cols)] for i in range(rows)]
    
    table = go.Figure(data=[go.Table(
        header=dict(values=[''] + col_labels,
                    fill_color='#1f77b4',
                    align='center',
                    font=dict(color='white', size=14)),
        cells=dict(values=[row_labels] + [[cell_text[i][j] for i in range(rows)] for j in range(cols)],
                   fill_color=[['#f0f0f0'] * rows] + cell_colors,
                   align='center',
                   font=dict(size=12)))
    ])
    table.update_layout(
        title=dict(text="Payoff Matrix (Player 1, Player 2)", font=dict(size=18)),
        margin=dict(l=10, r=10, t=50, b=10),
        width=500,
        height=300
    )
    return table

def validate_matrix_input(inputs, size):
    """Validate custom matrix input."""
    try:
        matrix = np.zeros((size, size))
        for i in range(size):
            for j in range(size):
                p1, p2 = map(float, inputs[i * size + j].split(','))
                matrix[i, j] = p1
        return matrix, None
    except:
        return None, "Invalid input. Use format 'x,y' for each cell."

def main():
    """Main Streamlit app with enhanced UI."""
    st.set_page_config(page_title="Nash Equilibrium Simulator", layout="wide", initial_sidebar_state="expanded")
    
    # Custom CSS for styling
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        .stButton>button { background-color: #1f77b4; color: white; border-radius: 8px; }
        .stButton>button:hover { background-color: #135ba1; }
        .sidebar .sidebar-content { background-color: #e9ecef; }
        h1 { color: #1f77b4; font-family: Arial, sans-serif; }
        h2, h3 { color: #2c3e50; }
        .st-expander { border: 1px solid #dee2e6; border-radius: 8px; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🎲 Nash Equilibrium Simulator")
    st.markdown("Analyze strategic interactions in 2-player games with interactive visualizations.")
    
    # Sidebar
    with st.sidebar:
        st.header("Game Configuration")
        game_choice = st.selectbox("Select Game", ["Prisoner's Dilemma", "Battle of the Sexes", "Matching Pennies", "Rock-Paper-Scissors", "Custom Game"], 
                                  help="Choose a predefined game or define your own payoff matrix.")
        
        if game_choice == "Custom Game":
            size = st.slider("Matrix Size", 2, 3, 2, help="Select 2x2 or 3x3 matrix.")
            st.subheader(f"Custom {size}x{size} Payoff Matrix")
            st.markdown("Enter payoffs as 'Player 1, Player 2' for each cell.")
            
            row_labels = [st.text_input(f"Row {i+1} Label", f"Row {i+1}") for i in range(size)]
            col_labels = [st.text_input(f"Column {j+1} Label", f"Column {j+1}") for j in range(size)]
            
            payoff_inputs = []
            cols = st.columns(size)
            for i in range(size):
                for j in range(cols):
                    with cols[j]:
                        payoff_inputs.append(st.text_input(f"({row_labels[i]}, {col_labels[j]})", "0,0"))
            
            description = st.text_area("Game Description", "Custom strategic game", help="Describe the game context.")
            
            if st.button("Analyze Custom Game"):
                payoff_player1, error1 = validate_matrix_input(payoff_inputs[::2], size)
                payoff_player2, error2 = validate_matrix_input(payoff_inputs[1::2], size)
                if error1 or error2:
                    st.error(error1 or error2)
                    return
        else:
            game = GAMES[game_choice]
            description = game["description"]
            payoff_player1 = np.array(game["payoff_player1"])
            payoff_player2 = np.array(game["payoff_player2"])
            row_labels = game["row_labels"]
            col_labels = game["col_labels"]
    
    # Main layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Game Description")
        st.markdown(description)
        
        st.header("Strategic Analysis")
        analysis = analyze_equilibria(payoff_player1, payoff_player2, row_labels, col_labels)
        st.markdown(analysis)
        
        if game_choice != "Rock-Paper-Scissors":  # Best response plot for 2x2 games only
            st.header("Best Response Functions")
            br_plot = plot_best_response(payoff_player1, payoff_player2, row_labels, col_labels)
            if br_plot:
                st.plotly_chart(br_plot, use_container_width=True)
            else:
                st.info("Best response plot available only for 2x2 games.")
    
    with col2:
        st.header("Payoff Matrix")
        nash_equilibria = find_pure_nash_equilibria(payoff_player1, payoff_player2)
        table = create_payoff_table(payoff_player1, payoff_player2, row_labels, col_labels, nash_equilibria)
        st.plotly_chart(table, use_container_width=True)
        
        # Download PDF report
        st.header("Download Analysis")
        pdf_content = latex_generator.generate_latex_report(game_choice, description, payoff_player1, payoff_player2, 
                                                          row_labels, col_labels, analysis)
        st.download_button(
            label="Download PDF Report",
            data=pdf_content,
            file_name=f"{game_choice}_analysis.tex",
            mime="text/plain",
            help="Download a LaTeX file summarizing the game analysis."
        )
    
    # Educational content
    with st.expander("Learn About Game Theory"):
        st.markdown("""
        **Nash Equilibrium**: A state where no player can improve their payoff by unilaterally changing their strategy.
        - **Pure Strategy**: Players choose a single action with certainty.
        - **Mixed Strategy**: Players randomize over actions with specific probabilities.
        
        **Dominant Strategy**: A strategy that is always best, regardless of the opponent's actions.
        
        **Pareto Optimality**: An outcome where no player can be made better off without harming another.
        
        **Stability**: Single equilibria or dominant strategies are stable; multiple equilibria may lead to coordination issues.
        
        **Best Response Plot**: Shows where players' best strategies intersect, indicating equilibria (for 2x2 games).
        
        Green cells in the matrix highlight pure strategy Nash equilibria.
        """)

if __name__ == "__main__":
    main()