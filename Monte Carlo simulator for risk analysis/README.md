Monte Carlo Simulation for Investment Portfolio Risk Analysis
A Python project to perform Monte Carlo simulation for analyzing risks in an investment portfolio.
Scenario
The system models a portfolio with 60% stocks (8% expected return, 15% volatility) and 40% bonds (4% expected return, 5% volatility) over a 1-year horizon, starting with $100,000. It simulates 10,000 scenarios to estimate final portfolio value distributions.
Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save monte_carlo_simulation.py, simulation_config.json, requirements.txt.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the Simulation:
Run: python monte_carlo_simulation.py
Output includes a console summary, simulation_report.txt, and visualizations in plots/.


View Results:
Check console for mean, standard deviation, percentiles (P5, P50, P95), and probability of loss.
Open simulation_report.txt for a detailed summary.
View visualizations in plots/:
portfolio_distribution.png: Histogram of final portfolio values.
portfolio_cdf.png: Cumulative distribution function.
portfolio_violin.png: Violin plot of outcomes.





Interpreting Results

Mean Portfolio Value: Expected final value after 1 year.
Standard Deviation: Measure of portfolio value variability.
Percentiles (P5, P50, P95): 5th, 50th (median), and 95th percentiles of outcomes.
Probability of Loss: Percentage of simulations where final value < initial investment.
Visualizations show the distribution and range of possible outcomes, with the initial investment ($100,000) marked.

Notes

Runs in ~30 seconds on a standard CPU.
Simulates 10,000 scenarios using normal distributions for stock and bond returns.
Configurable via simulation_config.json.
Outputs summary statistics and visualizations for risk analysis.
