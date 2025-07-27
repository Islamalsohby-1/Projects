Critical Path Method (CPM) Tool
This Python tool calculates the Critical Path for a project using the Critical Path Method (CPM). It accepts tasks either hardcoded or from a CSV file, computes task scheduling metrics, identifies the critical path, and visualizes the task graph.
Requirements

Python 3.8+
Dependencies listed in requirements.txt

Installation

Install dependencies:

pip install -r requirements.txt

Usage
Run the tool with the default mock project:
python cpm_tool.py

Or with a custom CSV file:
python cpm_tool.py sample_project.csv

CSV File Format
The CSV file must have the following columns:

Task: Task name (e.g., A, B, C)
Duration: Task duration in days (integer)
Dependencies: Semicolon-separated list of task names that must complete before this task (e.g., A;B)

Example (sample_project.csv):
Task,Duration,Dependencies
A,5,
B,3,A
C,2,A
...

Output

Console output: Critical path, total project duration, and a table of task metrics (ES, EF, LS, LF, Slack)
Visualization: A graph showing tasks, dependencies, and the critical path (red edges)

Notes

The tool uses networkx for graph operations and matplotlib for visualization.
The project must be a Directed Acyclic Graph (DAG); cycles will cause an error.
The mock project includes 11 tasks for demonstration.
