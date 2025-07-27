Brain-Like Neural Network Simulation
A Python project simulating a small neural network inspired by biological brain functions with 5 interconnected neurons.
Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Install FFmpeg: Required for animation (https://ffmpeg.org/download.html).
Clone or Create Files: Save brain_like_network.py, neuron.py, visualizer.py, requirements.txt.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the Simulation:
Run: python brain_like_network.py
Output includes a log (neuron_activity_log.txt) and visualizations (plots/neuron_states.png, plots/network_animation.mp4).


View Results:
Check neuron_activity_log.txt for neuron firings and signal propagations.
View plots/neuron_states.png for neuron activation over time.
View plots/network_animation.mp4 for network firing animation.



Notes

Runs in ~1–2 minutes on a standard CPU.
Simulates 5 neurons over 50 time steps with random synaptic weights (0–1).
Neurons have thresholds, refractory periods, and signal decay.
Synaptic weight matrix is logged and visualized.
Visualizations show firing patterns and network dynamics.
