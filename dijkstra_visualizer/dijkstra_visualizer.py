# Enhanced 3D Visualization of Dijkstra's Algorithm
# Uses networkx for graph operations, matplotlib for 3D visualization, and numpy for coordinate calculations
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import defaultdict
import heapq
import numpy as np
from matplotlib import cm
import matplotlib.animation as animation

# Custom Dijkstra's algorithm implementation with detailed tracking
def dijkstra(graph, start):
    """
    Implements Dijkstra's algorithm to find shortest paths from a start node.
    Returns distances and predecessors for path reconstruction.
    """
    distances = {node: float('infinity') for node in graph.nodes}
    distances[start] = 0
    predecessors = {node: None for node in graph.nodes}
    visited = set()
    pq = [(0, start)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight['weight']
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    return distances, predecessors

# Helper function to reconstruct the shortest path
def get_path(predecessors, end):
    """Reconstructs the shortest path from predecessors dictionary."""
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = predecessors[current]
    return path[::-1]

# Function to create a more complex sample graph
def create_sample_graph():
    """Creates a complex directed graph with weighted edges."""
    G = nx.DiGraph()
    edges = [
        ('A', 'B', 4), ('A', 'C', 2), ('A', 'F', 7),
        ('B', 'D', 3), ('B', 'C', 1), ('B', 'E', 6),
        ('C', 'B', 1), ('C', 'D', 5), ('C', 'E', 8),
        ('D', 'E', 2), ('D', 'F', 4), ('D', 'G', 9),
        ('E', 'D', 2), ('E', 'G', 3), ('E', 'H', 5),
        ('F', 'A', 7), ('F', 'G', 2), ('F', 'H', 6),
        ('G', 'E', 3), ('G', 'H', 2), ('H', 'F', 6)
    ]
    G.add_weighted_edges_from(edges)
    return G

# Main visualization function with enhanced 3D effects
def visualize_dijkstra_3d_enhanced():
    """Creates an enhanced 3D visualization of Dijkstra's algorithm with animation."""
    # Create graph
    G = create_sample_graph()
    start_node = 'A'
    
    # Run Dijkstra's algorithm
    distances, predecessors = dijkstra(G, start_node)
    
    # Print detailed results
    print("\n=== Shortest Path Analysis from Node", start_node, "===\n")
    for node, dist in distances.items():
        if dist != float('infinity'):
            path = get_path(predecessors, node)
            print(f"To {node}: Distance = {dist:.1f}, Path = {' -> '.join(path)}")
        else:
            print(f"To {node}: No path exists")
    print("\n=================================\n")
    
    # Set up 3D plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Generate 3D positions with spring layout
    pos = nx.spring_layout(G, dim=3, seed=42)
    
    # Normalize positions for better visualization
    coords = np.array([pos[node] for node in G.nodes])
    coords = (coords - coords.min()) / (coords.max() - coords.min()) * 2 - 1
    
    # Create node color gradient based on distance
    max_dist = max([d for d in distances.values() if d != float('infinity')] + [1])
    node_colors = [cm.viridis(distances[node] / max_dist if distances[node] != float('infinity') else 0) for node in G.nodes]
    
    # Draw nodes with size variation
    node_sizes = [800 if node == start_node else 400 for node in G.nodes]
    ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], c=node_colors, s=node_sizes, alpha=0.9, edgecolors='black')
    
    # Draw all edges
    for edge in G.edges:
        x = [pos[edge[0]][0], pos[edge[1]][0]]
        y = [pos[edge[0]][1], pos[edge[1]][1]]
        z = [pos[edge[0]][2], pos[edge[1]][2]]
        ax.plot(x, y, z, c='gray', linestyle='-', linewidth=1, alpha=0.5)
        
        # Add edge weight labels with enhanced styling
        mid_x = (x[0] + x[1]) / 2
        mid_y = (y[0] + y[1]) / 2
        mid_z = (z[0] + z[1]) / 2
        weight = G[edge[0]][edge[1]]['weight']
        ax.text(mid_x, mid_y, mid_z, f'{weight:.1f}', color='black', fontsize=8, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Prepare shortest path edges for animation
    path_edges = []
    for end_node in G.nodes:
        if end_node != start_node and distances[end_node] != float('infinity'):
            path = get_path(predecessors, end_node)
            path_edges.extend(list(zip(path[:-1], path[1:])))
    
    # Animation function
    def update(frame):
        ax.clear()
        ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], c=node_colors, s=node_sizes, alpha=0.9, edgecolors='black')
        
        # Redraw all edges
        for edge in G.edges:
            x = [pos[edge[0]][0], pos[edge[1]][0]]
            y = [pos[edge[0]][1], pos[edge[1]][1]]
            z = [pos[edge[0]][2], pos[edge[1]][2]]
            ax.plot(x, y, z, c='gray', linestyle='-', linewidth=1, alpha=0.5)
            
        # Highlight path edges up to current frame
        for edge in path_edges[:frame]:
            x = [pos[edge[0]][0], pos[edge[1]][0]]
            y = [pos[edge[0]][1], pos[edge[1]][1]]
            z = [pos[edge[0]][2], pos[edge[1]][2]]
            ax.plot(x, y, z, c='red', linewidth=3, alpha=0.9)
        
        # Redraw edge labels
        for edge in G.edges:
            x = [pos[edge[0]][0], pos[edge[1]][0]]
            y = [pos[edge[0]][1], pos[edge[1]][1]]
            z = [pos[edge[0]][2], pos[edge[1]][2]]
            mid_x = (x[0] + x[1]) / 2
            mid_y = (y[0] + y[1]) / 2
            mid_z = (z[0] + z[1]) / 2
            weight = G[edge[0]][edge[1]]['weight']
            ax.text(mid_x, mid_y, mid_z, f'{weight:.1f}', color='black', fontsize=8, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        
        # Redraw node labels
        for i, node in enumerate(G.nodes):
            ax.text(coords[i, 0], coords[i, 1], coords[i, 2], node, fontsize=10, fontweight='bold', color='darkblue')
        
        ax.set_title(f"Dijkstra's Algorithm - Shortest Paths from {start_node} (3D)")
        ax.set_axis_off()
        return ax,

    # Create animation
    ani = animation.FuncAnimation(fig, update, frames=len(path_edges) + 5, interval=500, blit=False)
    
    # Enhance 3D appearance
    ax.set_title(f"Dijkstra's Algorithm - Shortest Paths from {start_node} (3D)", fontsize=14, pad=20)
    ax.set_axis_off()
    ax.view_init(elev=20, azim=45)
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cm.viridis, norm=plt.Normalize(vmin=0, vmax=max_dist))
    plt.colorbar(sm, ax=ax, label='Distance from Source', pad=0.1)
    
    # Show plot
    plt.tight_layout()
    plt.show()

# Run the visualization
if __name__ == "__main__":
    visualize_dijkstra_3d_enhanced()