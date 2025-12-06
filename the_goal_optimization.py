"""
The Goal - Production Scheduling Optimization
"""
from pulp import *
import pandas as pd

def create_goal_optimization_model(
    heat_treatment_capacity=160,
    machining_capacity=200,
    assembly_capacity=180,
    demand_a=50,
    demand_b=80,
    profit_a=90,
    profit_b=60
):
    """Create and solve the production optimization model."""
    
    # Create model
    model = LpProblem("The_Goal", LpMaximize)
    
    # Decision variables
    product_a = LpVariable("Product_A", lowBound=0, cat='Continuous')
    product_b = LpVariable("Product_B", lowBound=0, cat='Continuous')
    
    # Objective function
    model += profit_a * product_a + profit_b * product_b
    
    # Processing times (hours per unit)
    machining_time = {"A": 2.5, "B": 1.5}
    heat_treatment_time = {"A": 4.0, "B": 2.0}
    assembly_time = {"A": 2.0, "B": 1.5}
    
    # Constraints
    model += machining_time["A"] * product_a + machining_time["B"] * product_b <= machining_capacity
    model += heat_treatment_time["A"] * product_a + heat_treatment_time["B"] * product_b <= heat_treatment_capacity
    model += assembly_time["A"] * product_a + assembly_time["B"] * product_b <= assembly_capacity
    model += product_a <= demand_a
    model += product_b <= demand_b
    
    # Solve
    model.solve(PULP_CBC_CMD(msg=0))
    
    # Prepare results
    results = {
        "status": LpStatus[model.status],
        "product_a": value(product_a),
        "product_b": value(product_b),
        "total_throughput": value(model.objective),
        "machining_used": machining_time["A"] * value(product_a) + machining_time["B"] * value(product_b),
        "machining_capacity": machining_capacity,
        "heat_treatment_used": heat_treatment_time["A"] * value(product_a) + heat_treatment_time["B"] * value(product_b),
        "heat_treatment_capacity": heat_treatment_capacity,
        "assembly_used": assembly_time["A"] * value(product_a) + assembly_time["B"] * value(product_b),
        "assembly_capacity": assembly_capacity,
    }
    
    # Calculate utilization
    results["machining_utilization"] = (results["machining_used"] / machining_capacity) * 100
    results["heat_treatment_utilization"] = (results["heat_treatment_used"] / heat_treatment_capacity) * 100
    results["assembly_utilization"] = (results["assembly_used"] / assembly_capacity) * 100
    
    # Identify bottleneck
    if results["heat_treatment_utilization"] >= 99.9:
        results["bottleneck"] = "Heat Treatment"
    elif results["machining_utilization"] >= 99.9:
        results["bottleneck"] = "Machining"
    elif results["assembly_utilization"] >= 99.9:
        results["bottleneck"] = "Assembly"
    else:
        results["bottleneck"] = "Demand"
    
    # Shadow prices
    constraints_data = []
    for name, constraint in model.constraints.items():
        constraints_data.append({
            "Constraint": name,
            "Shadow_Price": constraint.pi,
            "Slack": constraint.slack
        })
    results["constraints_df"] = pd.DataFrame(constraints_data)
    
    return results, model
