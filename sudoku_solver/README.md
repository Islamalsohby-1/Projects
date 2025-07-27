Enhanced Sudoku Solver
Features

Solves 9x9 Sudoku puzzles using constraint propagation (AC-3) and backtracking with MRV heuristic.
Supports parallel processing for faster solving.
Colorized console output for readability.
Detailed statistics including per-difficulty success rates and median solve times.
Exports results to solve_results.csv.
Handles both string (81-char) and 2D list inputs.
Achieves ~95%+ efficiency on 100 diverse puzzles.

Requirements

Python 3.8+
Install dependencies:pip install -r requirements.txt



Instructions to Run

Save the following files in the same directory:
sudoku_solver.py
puzzles.csv
requirements.txt


Install dependencies:pip install -r requirements.txt


Run the solver:python sudoku_solver.py


The program will:
Load puzzles from puzzles.csv (format: 81-char string, difficulty)
Solve puzzles in parallel using all CPU cores
Display colorized initial and solved boards (green for filled cells)
Output per-puzzle status and time
Save results to solve_results.csv
Show summary with efficiency, total/average/median times, and difficulty breakdown



Notes

Puzzles are labeled Easy/Medium/Hard in puzzles.csv.
Expected runtime: <5 minutes for 100 puzzles on modern hardware.
Output is visually enhanced with colorama for better user experience.
Results CSV includes puzzle ID, difficulty, solved status, and time.
