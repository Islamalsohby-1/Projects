from dataclasses import dataclass
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

# Set plot style
plt.style.use('seaborn')

@dataclass
class InvestmentConfig:
    """Configuration for investment portfolio simulation."""
    initial_investment: float = 100000
    expected_return_stock: float = 0.08
    volatility_stock: float = 0.15
    expected_return_bond: float = 0.04
    volatility_bond: float = 0.05
    stock_allocation: float = 0.6
    num_simulations: int = 10000
    time_horizon: int = 1  # Years

class MonteCarloSimulator:
    def __init__(self, config_file='simulation_config.json'):
        """Initialize simulator with configuration."""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            self.config = InvestmentConfig(**config_data)
        except FileNotFoundError:
            self.config = InvestmentConfig()
        
        self.results = []

    def run_simulation(self):
        """Run Monte Carlo simulation for investment portfolio returns."""
        for _ in range(self.config.num_simulations):
            # Sample returns from normal distributions
            stock_return = np.random.normal(
                self.config.expected_return_stock,
                self.config.volatility_stock,
                self.config.time_horizon
            )[0]
            
            bond_return = np.random.normal(
                self.config.expected_return_bond,
                self.config.volatility_bond,
                self.config.time_horizon
            )[0]
            
            # Calculate portfolio return
            portfolio_return = (self.config.stock_allocation * stock_return + 
                              (1 - self.config.stock_allocation) * bond_return)
            final_value = self.config.initial_investment * (1 + portfolio_return)
            
            self.results.append(final_value)
        
        return self.results

    def analyze_results(self):
        """Analyze simulation results and compute statistics."""
        results = np.array(self.results)
        stats = {
            'mean': np.mean(results),
            'std': np.std(results),
            'p5': np.percentile(results, 5),
            'p50': np.percentile(results, 50),
            'p95': np.percentile(results, 95),
            'prob_loss': np.mean(results < self.config.initial_investment) * 100
        }
        return stats

    def visualize_results(self):
        """Generate visualizations for simulation results."""
        os.makedirs('plots', exist_ok=True)
        results = np.array(self.results)
        
        # Histogram of final portfolio values
        plt.figure(figsize=(10, 6))
        sns.histplot(results, bins=50, kde=True, color='skyblue')
        plt.axvline(self.config.initial_investment, color='red', linestyle='--', label='Initial Investment')
        plt.title('Distribution of Portfolio Values After 1 Year')
        plt.xlabel('Portfolio Value ($)')
        plt.ylabel('Frequency')
        plt.legend()
        plt.tight_layout()
        plt.savefig('plots/portfolio_distribution.png')
        plt.close()
        
        # Cumulative Distribution Function (CDF)
        sorted_results = np.sort(results)
        cdf = np.arange(1, len(sorted_results) + 1) / len(sorted_results)
        plt.figure(figsize=(10, 6))
        plt.plot(sorted_results, cdf, color='blue')
        plt.axvline(self.config.initial_investment, color='red', linestyle='--', label='Initial Investment')
        plt.title('Cumulative Distribution Function of Portfolio Values')
        plt.xlabel('Portfolio Value ($)')
        plt.ylabel('Cumulative Probability')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('plots/portfolio_cdf.png')
        plt.close()
        
        # Violin plot
        plt.figure(figsize=(8, 6))
        sns.violinplot(data=results, color='lightgreen')
        plt.axhline(self.config.initial_investment, color='red', linestyle='--', label='Initial Investment')
        plt.title('Violin Plot of Portfolio Values')
        plt.ylabel('Portfolio Value ($)')
        plt.legend()
        plt.tight_layout()
        plt.savefig('plots/portfolio_violin.png')
        plt.close()

    def save_report(self, stats):
        """Save summary report of simulation results."""
        with open('simulation_report.txt', 'w') as f:
            f.write("Monte Carlo Simulation Report\n")
            f.write("============================\n")
            f.write(f"Scenario: Investment Portfolio Return\n")
            f.write(f"Initial Investment: ${self.config.initial_investment:,.2f}\n")
            f.write(f"Number of Simulations: {self.config.num_simulations:,}\n")
            f.write(f"Time Horizon: {self.config.time_horizon} year(s)\n")
            f.write("\nSummary Statistics:\n")
            f.write(f"Mean Portfolio Value: ${stats['mean']:,.2f}\n")
            f.write(f"Standard Deviation: ${stats['std']:,.2f}\n")
            f.write(f"5th Percentile (P5): ${stats['p5']:,.2f}\n")
            f.write(f"Median (P50): ${stats['p50']:,.2f}\n")
            f.write(f"95th Percentile (P95): ${stats['p95']:,.2f}\n")
            f.write(f"Probability of Loss: {stats['prob_loss']:.2f}%\n")
            f.write("\nVisualizations saved in 'plots/' directory\n")

def main():
    """Run the Monte Carlo simulation and generate outputs."""
    simulator = MonteCarloSimulator()
    results = simulator.run_simulation()
    stats = simulator.analyze_results()
    
    # Print summary
    print("Monte Carlo Simulation Summary")
    print(f"Mean Portfolio Value: ${stats['mean']:,.2f}")
    print(f"Standard Deviation: ${stats['std']:,.2f}")
    print(f"5th Percentile (P5): ${stats['p5']:,.2f}")
    print(f"Median (P50): ${stats['p50']:,.2f}")
    print(f"95th Percentile (P95): ${stats['p95']:,.2f}")
    print(f"Probability of Loss: {stats['prob_loss']:.2f}%")
    print("Visualizations saved in 'plots/' directory")
    
    # Save visualizations and report
    simulator.visualize_results()
    simulator.save_report(stats)

if __name__ == '__main__':
    main()