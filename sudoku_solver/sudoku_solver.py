# Enhanced Sudoku Solver with Constraint Propagation, Parallel Processing, and Colorized Output
import time
import csv
import copy
from collections import defaultdict
import statistics
from multiprocessing import Pool, cpu_count
from colorama import init, Fore, Style
import os

# Initialize colorama for colored console output
init()

# Print Sudoku board with colorized formatting
def print_board(board, highlight=None):
    highlight = highlight or set()
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print(Fore.CYAN + "- - - - - - - - - - - -" + Style.RESET_ALL)
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print(Fore.CYAN + "|" + Style.RESET_ALL, end=" ")
            cell = board[i][j]
            if (i, j) in highlight:
                print(Fore.GREEN + f"{cell if cell != 0 else '.'}" + Style.RESET_ALL, end=" ")
            else:
                print(Fore.WHITE + f"{cell if cell != 0 else '.'}" + Style.RESET_ALL, end=" ")
        print()
    print()

# Validate number placement
def is_valid(board, row, col, num):
    for x in range(9):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if board[i][j] == num:
                return False
    return True

# Constraint propagation with AC-3
def ac3(board, domains):
    arcs = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
    queue = [(r1, c1, r2, c2) for r1 in range(9) for c1 in range(9) if board[r1][c1] == 0
             for r2 in range(9) for c2 in range(9) if board[r2][c2] == 0 and (r1, c1) != (r2, c2)
             and (r1 == r2 or c1 == c2 or (r1//3 == r2//3 and c1//3 == c2//3))]
    
    while queue:
        (r1, c1, r2, c2) = queue.pop(0)
        if revise(board, domains, r1, c1, r2, c2):
            if not domains[r1][c1]:
                return False
            # Add neighboring arcs
            for r3 in range(9):
                for c3 in range(9):
                    if (r3, c3) != (r1, c1) and (r3 == r1 or c3 == c1 or (r3//3 == r1//3 and c3//3 == c1//3)):
                        queue.append((r3, c3, r1, c1))
    return True

def revise(board, domains, r1, c1, r2, c2):
    revised = False
    if (r1 == r2 or c1 == c2 or (r1//3 == r2//3 and c1//3 == c2//3)):
        values = domains[r1][c1].copy()
        for x in values:
            if not any(is_valid(board, r2, c2, y) and y != x for y in domains[r2][c2]):
                domains[r1][c1].remove(x)
                revised = True
    return revised

# Find cell with Minimum Remaining Values (MRV)
def find_empty_mrv(board, domains):
    min_values = 10
    best_cell = None
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                values = len(domains[i][j])
                if values < min_values:
                    min_values = values
                    best_cell = (i, j)
    return best_cell

# Solve Sudoku using backtracking with constraint propagation
def solve_sudoku(board):
    # Initialize domains
    domains = [[{1,2,3,4,5,6,7,8,9} if board[i][j] == 0 else {board[i][j]} for j in range(9)] for i in range(9)]
    
    # Apply AC-3 initially
    if not ac3(board, domains):
        return False, board
    
    # If all cells have single values, assign them
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0 and len(domains[i][j]) == 1:
                board[i][j] = domains[i][j].pop()
    
    # Backtracking with MRV
    def backtrack(board, domains):
        empty = find_empty_mrv(board, domains)
        if not empty:
            return True
        row, col = empty
        
        for num in domains[row][col].copy():
            if is_valid(board, row, col, num):
                board[row][col] = num
                old_domains = copy.deepcopy(domains)
                domains[row][col] = {num}
                if ac3(board, domains) and backtrack(board, domains):
                    return True
                board[row][col] = 0
                domains = old_domains
        return False
    
    solved = backtrack(board, domains)
    return solved, board

# Parse puzzle from string or 2D list
def parse_puzzle(puzzle_input):
    if isinstance(puzzle_input, str):
        if len(puzzle_input) != 81:
            return None
        try:
            return [[int(puzzle_input[i * 9 + j]) for j in range(9)] for i in range(9)]
        except ValueError:
            return None
    elif isinstance(puzzle_input, list) and len(puzzle_input) == 9 and all(len(row) == 9 for row in puzzle_input):
        return [[x if isinstance(x, int) and 0 <= x <= 9 else 0 for x in row] for row in puzzle_input]
    return None

# Validate input board
def is_valid_board(board):
    if not board or len(board) != 9 or any(len(row) != 9 for row in board):
        return False
    for i in range(9):
        row_nums = [board[i][j] for j in range(9) if board[i][j] != 0]
        col_nums = [board[j][i] for j in range(9) if board[j][i] != 0]
        if len(row_nums) != len(set(row_nums)) or len(col_nums) != len(set(col_nums)):
            return False
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box_nums = [board[i][j] for i in range(box_row, box_row + 3) for j in range(box_col, box_col + 3) if board[i][j] != 0]
            if len(box_nums) != len(set(box_nums)):
                return False
    return True

# Load puzzles from CSV file
def load_puzzles(filename):
    puzzles = []
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:  # Expect puzzle string and difficulty
                    puzzle = parse_puzzle(row[0])
                    if puzzle and is_valid_board(puzzle):
                        puzzles.append((puzzle, row[1] if len(row) > 1 else 'Unknown'))
    except FileNotFoundError:
        print(Fore.RED + f"Error: {filename} not found." + Style.RESET_ALL)
    return puzzles

# Solve a single puzzle (for multiprocessing)
def solve_puzzle_task(args):
    idx, puzzle, difficulty = args
    board = copy.deepcopy(puzzle)
    start_time = time.time()
    solved, solved_board = solve_sudoku(board)
    solve_time = time.time() - start_time
    return idx, puzzle, solved_board, solved, solve_time, difficulty

# Main function
def main():
    # Load puzzles
    puzzles = load_puzzles('puzzles.csv')
    if not puzzles:
        print(Fore.RED + "No valid puzzles loaded. Exiting." + Style.RESET_ALL)
        return
    
    total_puzzles = len(puzzles)
    print(Fore.YELLOW + f"Loaded {total_puzzles} puzzles. Solving with {cpu_count()} CPU cores..." + Style.RESET_ALL)
    
    # Prepare tasks
    tasks = [(i + 1, puzzle, diff) for i, (puzzle, diff) in enumerate(puzzles)]
    
    # Solve puzzles in parallel
    solved_count = 0
    total_time = 0
    solve_times = []
    difficulty_stats = defaultdict(lambda: {'solved': 0, 'total': 0, 'times': []})
    results = []

    with Pool(processes=cpu_count()) as pool:
        results = pool.map(solve_puzzle_task, tasks)
    
    # Export results to CSV
    with open('solve_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Puzzle ID', 'Difficulty', 'Solved', 'Time (s)'])
        for idx, _, _, solved, solve_time, difficulty in sorted(results):
            writer.writerow([idx, difficulty, solved, f"{solve_time:.4f}"])
    
    # Process results
    for idx, original, solved_board, solved, solve_time, difficulty in sorted(results):
        difficulty_stats[difficulty]['total'] += 1
        difficulty_stats[difficulty]['times'].append(solve_time)
        if solved:
            solved_count += 1
            difficulty_stats[difficulty]['solved'] += 1
        total_time += solve_time
        solve_times.append(solve_time)
        
        print(Fore.YELLOW + f"\nPuzzle {idx} (Difficulty: {difficulty}):" + Style.RESET_ALL)
        print("Initial board:")
        print_board(original)
        print("Solved board:" if solved else "No solution found:")
        highlight = {(i, j) for i in range(9) for j in range(9) if original[i][j] == 0}
        print_board(solved_board, highlight)
        status = Fore.GREEN + "Solved" if solved else Fore.RED + "Failed"
        print(f"Status: {status}" + Style.RESET_ALL + f" | Time: {solve_time:.4f} seconds")
    
    # Summary statistics
    efficiency = (solved_count / total_puzzles) * 100 if total_puzzles > 0 else 0
    median_time = statistics.median(solve_times) if solve_times else 0
    
    print(Fore.YELLOW + "\nSummary:" + Style.RESET_ALL)
    print(f"Total puzzles attempted: {total_puzzles}")
    print(f"Total puzzles solved: {solved_count}")
    print(f"Efficiency rate: {efficiency:.2f}%")
    print(f"Total time taken: {total_time:.4f} seconds")
    print(f"Average time per puzzle: {total_time / total_puzzles:.4f} seconds" if total_puzzles > 0 else "No puzzles processed.")
    print(f"Median time per puzzle: {median_time:.4f} seconds")
    
    print(Fore.YELLOW + "\nDifficulty Breakdown:" + Style.RESET_ALL)
    for diff, stats in difficulty_stats.items():
        diff_efficiency = (stats['solved'] / stats['total']) * 100 if stats['total'] > 0 else 0
        avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
        print(f"{diff}: {stats['solved']}/{stats['total']} solved ({diff_efficiency:.2f}%), Avg time: {avg_time:.4f}s")

if __name__ == "__main__":
    main()