import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta
from optimizer import optimize_supply_chain

# Set plot style
plt.style.use('seaborn')

class SupplyChainSimulator:
    def __init__(self):
        """Initialize supply chain entities and parameters."""
        self.suppliers = ['S1', 'S2']
        self.warehouses = ['W1', 'W2', 'W3']
        self.customers = ['C1', 'C2', 'C3', 'C4', 'C5']
        self.days = 30
        
        # Transportation costs (S->W, W->C)
        self.cost_s_to_w = pd.DataFrame({
            'W1': [2, 3],
            'W2': [4, 2],
            'W3': [3, 4]
        }, index=['S1', 'S2'])
        
        self.cost_w_to_c = pd.DataFrame({
            'C1': [1, 2, 3],
            'C2': [2, 1, 2],
            'C3': [3, 2, 1],
            'C4': [2, 3, 2],
            'C5': [3, 1, 2]
        }, index=['W1', 'W2', 'W3'])
        
        # Warehouse capacities
        self.capacities = {'W1': 1000, 'W2': 800, 'W3': 1200}
        
        # Lead times (days)
        self.lead_times_s_to_w = pd.DataFrame({
            'W1': [1, 2],
            'W2': [2, 1],
            'W3': [1, 2]
        }, index=['S1', 'S2'])
        
        self.lead_times_w_to_c = pd.DataFrame({
            'C1': [1, 1, 2],
            'C2': [2, 1, 1],
            'C3': [1, 2, 1],
            'C4': [2, 1, 2],
            'C5': [1, 2, 1]
        }, index=['W1', 'W2', 'W3'])
        
        # Initialize inventory
        self.inventory = {w: self.capacities[w] // 2 for w in self.warehouses}
        self.inventory_history = []
        
        # Customer demand (load or simulate)
        self.demand = self.load_demand()
        
        # Log file
        self.log_file = 'supply_chain_log.txt'
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def load_demand(self):
        """Load or simulate customer demand."""
        if os.path.exists('data/customer_demand.csv'):
            df = pd.read_csv('data/customer_demand.csv')
        else:
            dates = [datetime(2025, 7, 1) + timedelta(days=i) for i in range(self.days)]
            demand = {c: np.random.randint(50, 200, size=self.days) for c in self.customers}
            df = pd.DataFrame(demand, index=dates)
            os.makedirs('data', exist_ok=True)
            df.to_csv('data/customer_demand.csv')
        return df

    def log_operation(self, day, message):
        """Append operation to log file."""
        with open(self.log_file, 'a') as f:
            f.write(f"Day {day}: {message}\n")

    def simulate_day(self, day, shipments_s_to_w, shipments_w_to_c):
        """Simulate one day of supply chain operations."""
        date = datetime(2025, 7, 1) + timedelta(days=day)
        
        # Process incoming shipments to warehouses
        for s in self.suppliers:
            for w in self.warehouses:
                qty = shipments_s_to_w.get((s, w), 0)
                if qty > 0:
                    self.inventory[w] += qty
                    self.log_operation(day, f"Shipped {qty} units from {s} to {w}")
        
        # Process customer demand
        fulfilled = {c: 0 for c in self.customers}
        delays = []
        for c in self.customers:
            demand = int(self.demand.loc[date, c])
            for w in self.warehouses:
                qty = shipments_w_to_c.get((w, c), 0)
                if qty > 0 and self.inventory[w] >= qty:
                    self.inventory[w] -= qty
                    fulfilled[c] += qty
                    delay = self.lead_times_w_to_c.loc[w, c] + np.random.randint(-1, 2)
                    delays.append(delay)
                    self.log_operation(day, f"Shipped {qty} units from {w} to {c} (demand: {demand}, delay: {delay} days)")
        
        # Check stockouts
        for c in self.customers:
            demand = int(self.demand.loc[date, c])
            if fulfilled[c] < demand:
                self.log_operation(day, f"Stockout at {c}: {demand - fulfilled[c]} units unfulfilled")
        
        # Record inventory levels
        self.inventory_history.append({w: self.inventory[w] for w in self.warehouses})
        
        return fulfilled, delays

    def run_simulation(self):
        """Run the supply chain simulation for 30 days."""
        total_cost = 0
        total_orders = 0
        fulfilled_orders = 0
        all_delays = []
        
        for day in range(self.days):
            date = datetime(2025, 7, 1) + timedelta(days=day)
            demand = {c: int(self.demand.loc[date, c]) for c in self.customers}
            
            # Optimize shipments
            shipments_s_to_w, shipments_w_to_c, day_cost = optimize_supply_chain(
                self.inventory, self.capacities, demand, 
                self.cost_s_to_w, self.cost_w_to_c,
                self.lead_times_s_to_w, self.lead_times_w_to_c
            )
            total_cost += day_cost
            
            # Simulate day
            fulfilled, delays = self.simulate_day(day, shipments_s_to_w, shipments_w_to_c)
            all_delays.extend(delays)
            
            # Update order statistics
            for c in self.customers:
                total_orders += 1
                if fulfilled[c] >= demand[c]:
                    fulfilled_orders += 1
            
            # Replenish inventory if low
            for w in self.warehouses:
                if self.inventory[w] < self.capacities[w] * 0.3:
                    self.log_operation(day, f"Low inventory at {w}: {self.inventory[w]}/{self.capacities[w]}")
        
        # Calculate metrics
        fulfillment_rate = (fulfilled_orders / total_orders) * 100 if total_orders > 0 else 0
        avg_delay = np.mean(all_delays) if all_delays else 0
        
        return total_cost, fulfillment_rate, avg_delay

    def plot_results(self, total_cost, fulfillment_rate, avg_delay):
        """Plot inventory trends and cost breakdown."""
        os.makedirs('plots', exist_ok=True)
        
        # Inventory trends
        inventory_df = pd.DataFrame(self.inventory_history, index=[f"Day {i+1}" for i in range(self.days)])
        plt.figure(figsize=(12, 6))
        for w in self.warehouses:
            plt.plot(inventory_df.index, inventory_df[w], label=w, marker='o')
        plt.title('Warehouse Inventory Levels Over Time')
        plt.xlabel('Day')
        plt.ylabel('Inventory (Units)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('plots/inventory_trends.png')
        plt.close()
        
        # Cost breakdown
        plt.figure(figsize=(8, 6))
        plt.bar(['Transportation Cost'], [total_cost], color='skyblue')
        plt.title('Supply Chain Cost Breakdown')
        plt.ylabel('Cost ($)')
        plt.tight_layout()
        plt.savefig('plots/cost_breakdown.png')
        plt.close()

    def save_report(self, total_cost, fulfillment_rate, avg_delay):
        """Save summary report."""
        with open('supply_chain_report.txt', 'w') as f:
            f.write(f"Supply Chain Simulation Report\n")
            f.write(f"{'='*30}\n")
            f.write(f"Total Transportation Cost: ${total_cost:.2f}\n")
            f.write(f"Order Fulfillment Rate: {fulfillment_rate:.2f}%\n")
            f.write(f"Average Delivery Delay: {avg_delay:.2f} days\n")
            f.write(f"Log saved to: {self.log_file}\n")
            f.write(f"Plots saved in: plots/\n")

def main():
    """Main function to run the supply chain simulation."""
    simulator = SupplyChainSimulator()
    total_cost, fulfillment_rate, avg_delay = simulator.run_simulation()
    
    # Print summary
    print("Supply Chain Simulation Summary")
    print(f"Total Transportation Cost: ${total_cost:.2f}")
    print(f"Order Fulfillment Rate: {fulfillment_rate:.2f}%")
    print(f"Average Delivery Delay: {avg_delay:.2f} days")
    print(f"Log saved to: {simulator.log_file}")
    print(f"Plots saved in: plots/")
    
    # Save results
    simulator.plot_results(total_cost, fulfillment_rate, avg_delay)
    simulator.save_report(total_cost, fulfillment_rate, avg_delay)

if __name__ == '__main__':
    main()