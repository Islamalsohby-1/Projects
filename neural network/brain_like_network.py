import numpy as np
from neuron import Neuron
from visualizer import plot_neuron_states, animate_network
import networkx as nx

class BrainLikeNetwork:
    def __init__(self, num_neurons=5, time_steps=50):
        """Initialize the neural network with specified number of neurons and time steps."""
        self.num_neurons = num_neurons
        self.time_steps = time_steps
        self.neurons = [Neuron(i, threshold=1.0, refractory_period=2) for i in range(num_neurons)]
        
        # Synaptic weight matrix (5x5, asymmetric, random weights between 0 and 1)
        self.weights = np.random.uniform(0, 1, (num_neurons, num_neurons))
        np.fill_diagonal(self.weights, 0)  # No self-connections
        
        # Log for activations and signals
        self.activation_log = np.zeros((time_steps, num_neurons))
        self.signal_log = []

    def simulate(self):
        """Run the neural network simulation."""
        # Initial random input to kickstart simulation
        initial_input = np.random.uniform(0, 0.5, self.num_neurons)
        for i, neuron in enumerate(self.neurons):
            neuron.receive_input(initial_input[i], 0)
        
        for t in range(self.time_steps):
            signals = np.zeros(self.num_neurons)
            for i, neuron in enumerate(self.neurons):
                # Process input and check if neuron fires
                fired = neuron.process(t)
                self.activation_log[t, i] = 1 if fired else 0
                if fired:
                    signals[i] = 1.0
            
            # Propagate signals to connected neurons
            for i, neuron in enumerate(self.neurons):
                for j in range(self.num_neurons):
                    if signals[i] > 0 and self.weights[i, j] > 0:
                        self.neurons[j].receive_input(signals[i] * self.weights[i, j], t + 1)
                        self.signal_log.append((t, i, j, self.weights[i, j]))
            
            # Log signals for this time step
            if any(signals):
                self.signal_log.append((t, "Fired", [i for i, s in enumerate(signals) if s > 0]))

        # Save log to file
        with open('neuron_activity_log.txt', 'w') as f:
            f.write("Neuron Activity Log\n")
            f.write("=================\n")
            f.write("Synaptic Weight Matrix:\n")
            f.write(str(self.weights) + "\n\n")
            f.write("Time Step | Firing Neurons | Signal Propagation\n")
            for t in range(self.time_steps):
                fired = [i for i, a in enumerate(self.activation_log[t]) if a > 0]
                f.write(f"T={t:02d} | {fired if fired else 'None'} | ")
                signals = [s for s in self.signal_log if s[0] == t and len(s) == 4]
                f.write(f"{[(f'N{s[1]}->N{s[2]}', s[3]) for s in signals]}\n")

    def visualize(self):
        """Visualize neuron states and network animation."""
        # Plot neuron states over time
        plot_neuron_states(self.activation_log, self.time_steps, self.num_neurons)
        
        # Create network graph for animation
        G = nx.DiGraph()
        G.add_nodes_from(range(self.num_neurons))
        for i in range(self.num_neurons):
            for j in range(self.num_neurons):
                if self.weights[i, j] > 0:
                    G.add_edge(i, j, weight=self.weights[i, j])
        
        animate_network(G, self.activation_log, self.signal_log)

def main():
    """Run the neural network simulation and visualization."""
    network = BrainLikeNetwork()
    network.simulate()
    network.visualize()
    print("Simulation complete. Check 'neuron_activity_log.txt' for activity log.")
    print("Visualizations saved in 'plots/neuron_states.png' and 'plots/network_animation.mp4'.")

if __name__ == '__main__':
    main()