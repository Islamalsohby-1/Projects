import numpy as np
from scipy.optimize import linprog

def optimize_supply_chain(inventory, capacities, demand, cost_s_to_w, cost_w_to_c, lead_times_s_to_w, lead_times_w_to_c):
    """Optimize daily shipments to minimize transportation cost."""
    suppliers = list(cost_s_to_w.index)
    warehouses = list(cost_s_to_w.columns)
    customers = list(cost_w_to_c.columns)
    
    # Decision variables: S->W and W->C shipments
    num_s_to_w = len(suppliers) * len(warehouses)
    num_w_to_c = len(warehouses) * len(customers)
    num_vars = num_s_to_w + num_w_to_c
    
    # Objective: Minimize total transportation cost
    costs = np.concatenate([
        cost_s_to_w.values.flatten(),
        cost_w_to_c.values.flatten()
    ])
    
    # Constraints
    A_eq = []
    b_eq = []
    
    # Warehouse inventory balance
    for w in warehouses:
        w_idx = warehouses.index(w)
        row = np.zeros(num_vars)
        # Incoming from suppliers
        for s in suppliers:
            s_idx = suppliers.index(s)
            row[s_idx * len(warehouses) + w_idx] = 1
        # Outgoing to customers
        for c in customers:
            c_idx = customers.index(c)
            row[num_s_to_w + w_idx * len(customers) + c_idx] = -1
        A_eq.append(row)
        b_eq.append(inventory[w])
    
    # Customer demand fulfillment
    for c in customers:
        c_idx = customers.index(c)
        row = np.zeros(num_vars)
        for w in warehouses:
            w_idx = warehouses.index(w)
            row[num_s_to_w + w_idx * len(customers) + c_idx] = 1
        A_eq.append(row)
        b_eq.append(demand[c])
    
    # Bounds: Non-negative shipments, warehouse capacity
    bounds = [(0, None)] * num_s_to_w + [(0, None)] * num_w_to_c
    for w in warehouses:
        w_idx = warehouses.index(w)
        incoming = [(0, capacities[w] - inventory[w])] * len(suppliers)
        bounds[w_idx:len(suppliers) * len(warehouses):len(warehouses)] = incoming
    
    # Solve linear program
    result = linprog(costs, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if not result.success:
        return {}, {}, 0
    
    # Extract shipments
    shipments_s_to_w = {}
    shipments_w_to_c = {}
    for s_idx, s in enumerate(suppliers):
        for w_idx, w in enumerate(warehouses):
            qty = result.x[s_idx * len(warehouses) + w_idx]
            if qty > 0:
                shipments_s_to_w[(s, w)] = qty
    
    for w_idx, w in enumerate(warehouses):
        for c_idx, c in enumerate(customers):
            qty = result.x[num_s_to_w + w_idx * len(customers) + c_idx]
            if qty > 0:
                shipments_w_to_c[(w, c)] = qty
    
    total_cost = result.fun if result.success else 0
    return shipments_s_to_w, shipments_w_to_c, total_cost