Supply Chain Simulator
A Python project to simulate and optimize a supply chain system with suppliers, warehouses, and customers.
Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save supply_chain_simulator.py, optimizer.py, requirements.txt, and optionally data/customer_demand.csv.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the Simulation:
Run: python supply_chain_simulator.py
Output includes a console summary, supply_chain_report.txt, supply_chain_log.txt, and plots in plots/.


View Results:
Check the console for total cost, fulfillment rate, and average delay.
Open supply_chain_report.txt for a summary.
View supply_chain_log.txt for daily operations.
Check plots/inventory_trends.png and plots/cost_breakdown.png for visualizations.



Notes

Runs in ~5–10 minutes with a standard Python setup.
Simulates 2 suppliers, 3 warehouses, and 5 customers over 30 days.
Optimizes transportation costs and minimizes delays using linear programming.
Demand is loaded from data/customer_demand.csv or simulated if absent.
Plots show inventory trends and cost breakdown.
