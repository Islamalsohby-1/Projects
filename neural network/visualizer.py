import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.animation as animation
import numpy as np
import os

# Set plot style
plt.style.use('seaborn')

def plot_neuron_states(activation_log, time_steps, num_neurons):
    """Plot neuron activation states over time."""
    os.makedirs('plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    for i in range(num_neurons):
        plt.plot(range(time_steps), activation_log[:, i], label=f'Neuron {i}', marker='o')
    plt.title('Neuron Activation States Over Time')
    plt.xlabel('Time Step')
    plt.ylabel('Activation (1 = Fired, 0 = Inactive)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('plots/neuron_states.png')
    plt.close()

def animate_network(G, activation_log, signal_log):
    """Create an animation of the neural network firing."""
    fig, ax = plt.subplots(figsize=(8, 8))
    pos = nx.spring_layout(G, seed=42)
    
    def update(t):
        ax.clear()
        # Node colors based on activation
        node_colors = ['red' if activation_log[t, i] > 0 else 'lightblue' for i in range(len(G.nodes))]
        
        # Edge colors based on signal propagation
        edge_colors = ['gray'] * len(G.edges)
        active_edges = [(s[1], s[2]) for s in signal_log if s[0] == t and len(s) == 4]
        for i, (u, v, _) in enumerate(G.edges):
            if (u, v) in active_edges:
                edge_colors[i] = 'red'
        
        nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, 
                edge_color=edge_colors, node_size=500, font_size=10, 
                font_color='white', font_weight='bold')
        ax.set_title(f'Neural Network at Time Step {t}')
    
    ani = animation.FuncAnimation(fig, update, frames=len(activation_log), interval=500, repeat=False)
    ani.save('plots/network_animation.mp4', writer='ffmpeg')
    plt.close()