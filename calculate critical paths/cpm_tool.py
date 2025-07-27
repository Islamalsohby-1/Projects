import csv
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import sys
from typing import List, Dict, Tuple

class Task:
    def __init__(self, name: str, duration: int, dependencies: List[str]):
        self.name = name
        self.duration = duration
        self.dependencies = dependencies
        self.es = 0
        self.ef = 0
        self.ls = 0
        self.lf = 0
        self.slack = 0

def load_tasks(file_path: str = None) -> List[Task]:
    tasks = []
    if file_path:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                deps = row['Dependencies'].split(';') if row['Dependencies'] else []
                tasks.append(Task(row['Task'], int(row['Duration']), deps))
    else:
        # Mock project data
        mock_data = [
            ('A', 5, []),
            ('B', 3, ['A']),
            ('C', 2, ['A']),
            ('D', 4, ['B']),
            ('E', 6, ['B', 'C']),
            ('F', 3, ['C']),
            ('G', 5, ['D', 'E']),
            ('H', 2, ['E', 'F']),
            ('I', 4, ['F']),
            ('J', 3, ['G']),
            ('K', 2, ['H', 'I']),
        ]
        for name, duration, deps in mock_data:
            tasks.append(Task(name, duration, deps))
    return tasks

def build_graph(tasks: List[Task]) -> nx.DiGraph:
    G = nx.DiGraph()
    for task in tasks:
        G.add_node(task.name, duration=task.duration)
        for dep in task.dependencies:
            G.add_edge(dep, task.name)
    return G

def forward_pass(tasks: List[Task], G: nx.DiGraph) -> Dict[str, Task]:
    task_map = {task.name: task for task in tasks}
    for node in nx.topological_sort(G):
        task = task_map[node]
        task.es = max([task_map[pred].ef for pred in G.predecessors(node)], default=0)
        task.ef = task.es + task.duration
    return task_map

def backward_pass(tasks: List[Task], G: nx.DiGraph, task_map: Dict[str, Task]) -> Tuple[Dict[str, Task], float]:
    project_duration = max(task.ef for task in tasks)
    for task in tasks:
        task.lf = project_duration
        task.ls = task.lf - task.duration
    for node in reversed(list(nx.topological_sort(G))):
        task = task_map[node]
        task.lf = min([task_map[succ].ls for succ in G.successors(node)], default=project_duration)
        task.ls = task.lf - task.duration
        task.slack = task.ls - task.es
    return task_map, project_duration

def find_critical_path(G: nx.DiGraph, task_map: Dict[str, Task]) -> List[str]:
    critical_path = []
    for node in nx.topological_sort(G):
        if task_map[node].slack == 0:
            critical_path.append(node)
    return critical_path

def print_results(tasks: List[Task], critical_path: List[str], project_duration: float):
    print("\nCritical Path Method Results")
    print(f"Critical Path: {' -> '.join(critical_path)}")
    print(f"Total Project Duration: {project_duration} days")
    print("\nTask Details:")
    print(f"{'Task':<6} {'Duration':<10} {'ES':<6} {'EF':<6} {'LS':<6} {'LF':<6} {'Slack':<6}")
    print("-" * 40)
    for task in sorted(tasks, key=lambda x: x.name):
        print(f"{task.name:<6} {task.duration:<10} {task.es:<6} {task.ef:<6} {task.ls:<6} {task.lf:<6} {task.slack:<6}")

def visualize_graph(G: nx.DiGraph, task_map: Dict[str, Task], critical_path: List[str]):
    pos = nx.spring_layout(G)
    edge_colors = ['red' if (u, v) in [(critical_path[i], critical_path[i+1]) for i in range(len(critical_path)-1)] else 'black' for u, v in G.edges()]
    node_labels = {node: f"{node}\n{task_map[node].duration}d" for node in G.nodes()}
    
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, labels=node_labels, node_color='lightblue', 
            node_size=500, font_size=10, edge_color=edge_colors, arrows=True)
    plt.title("Project Task Graph (Critical Path in Red)")
    plt.show()

def main(file_path: str = None):
    tasks = load_tasks(file_path)
    G = build_graph(tasks)
    if not nx.is_directed_acyclic_graph(G):
        print("Error: The project graph contains cycles!")
        return
    task_map = forward_pass(tasks, G)
    task_map, project_duration = backward_pass(tasks, G, task_map)
    critical_path = find_critical_path(G, task_map)
    print_results(tasks, critical_path, project_duration)
    visualize_graph(G, task_map, critical_path)

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(file_path)