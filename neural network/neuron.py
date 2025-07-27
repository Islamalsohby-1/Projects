import numpy as np

class Neuron:
    def __init__(self, neuron_id, threshold=1.0, refractory_period=2):
        """Initialize a neuron with given parameters."""
        self.id = neuron_id
        self.threshold = threshold
        self.refractory_period = refractory_period
        self.input_buffer = []  # List of (input_value, time) tuples
        self.last_fired = -refractory_period - 1  # Allow firing at t=0
        self.decay_rate = 0.1  # Signal decay per time step

    def receive_input(self, input_value, time):
        """Add input signal to buffer for processing at specified time."""
        self.input_buffer.append((input_value, time))

    def process(self, current_time):
        """Process inputs and determine if neuron fires."""
        # Check if in refractory period
        if current_time - self.last_fired <= self.refractory_period:
            return False
        
        # Sum inputs for current time with decay
        total_input = 0
        new_buffer = []
        for value, t in self.input_buffer:
            decayed_value = value * np.exp(-self.decay_rate * (current_time - t))
            if t <= current_time:
                total_input += decayed_value
            else:
                new_buffer.append((value, t))
        self.input_buffer = new_buffer
        
        # Fire if total input exceeds threshold
        if total_input >= self.threshold:
            self.last_fired = current_time
            return True
        return False