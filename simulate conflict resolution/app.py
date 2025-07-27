from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Load scenarios from JSON file
def load_scenarios():
    with open('scenarios.json', 'r') as f:
        return json.load(f)

scenarios = load_scenarios()

@app.route('/')
def index():
    return render_template('index.html', scenarios=scenarios)

@app.route('/scenario/<int:scenario_id>')
def get_scenario(scenario_id):
    return jsonify(scenarios[scenario_id])

@app.route('/choice', methods=['POST'])
def make_choice():
    data = request.form
    scenario_id = int(data['scenario_id'])
    choice_id = data['choice_id']
    # Navigate through the decision tree
    current_scenario = scenarios[scenario_id]
    current_step = current_scenario['steps']
    for cid in choice_id.split('.'):
        current_step = current_step[int(cid)]['next']
    return jsonify(current_step)

if __name__ == '__main__':
    app.run(debug=True)