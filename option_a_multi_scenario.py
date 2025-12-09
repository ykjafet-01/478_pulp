"""
Option A: Multi-Scenario Comparison
"""
import streamlit as st
import plotly.graph_objects as go
from the_goal_optimization import create_goal_optimization_model

st.set_page_config(page_title="Multi-Scenario Comparison", layout="wide")

st.title("🏭 The Goal: Multi-Scenario Comparison - Congratilations Jafet!!!")
st.info("**What Python Can Do That Excel Cannot:** Compare 3 scenarios simultaneously with automatic insights!")

# Initialize scenarios
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = {
        'scenario1': {'name': 'Baseline', 'heat_treatment': 160, 'machining': 200, 'assembly': 180, 'demand_a': 50, 'demand_b': 80, 'profit_a': 90, 'profit_b': 60},
        'scenario2': {'name': 'Elevate Bottleneck', 'heat_treatment': 200, 'machining': 200, 'assembly': 180, 'demand_a': 50, 'demand_b': 80, 'profit_a': 90, 'profit_b': 60},
        'scenario3': {'name': 'Premium Product A', 'heat_treatment': 160, 'machining': 200, 'assembly': 180, 'demand_a': 50, 'demand_b': 80, 'profit_a': 140, 'profit_b': 60}
    }

# Sidebar
st.sidebar.header("Configure Scenarios")
selected = st.sidebar.radio("Edit Scenario:", ['scenario1', 'scenario2', 'scenario3'], 
                            format_func=lambda x: st.session_state.scenarios[x]['name'])

st.sidebar.subheader(f"Edit: {st.session_state.scenarios[selected]['name']}")
st.session_state.scenarios[selected]['name'] = st.sidebar.text_input("Name:", value=st.session_state.scenarios[selected]['name'], key=f"n_{selected}")
st.session_state.scenarios[selected]['heat_treatment'] = st.sidebar.slider("Heat Treatment:", 80, 240, st.session_state.scenarios[selected]['heat_treatment'], 10, key=f"h_{selected}")
st.session_state.scenarios[selected]['machining'] = st.sidebar.slider("Machining:", 100, 300, st.session_state.scenarios[selected]['machining'], 10, key=f"m_{selected}")
st.session_state.scenarios[selected]['assembly'] = st.sidebar.slider("Assembly:", 100, 300, st.session_state.scenarios[selected]['assembly'], 10, key=f"a_{selected}")
st.session_state.scenarios[selected]['demand_a'] = st.sidebar.slider("Demand A:", 0, 100, st.session_state.scenarios[selected]['demand_a'], 5, key=f"da_{selected}")
st.session_state.scenarios[selected]['demand_b'] = st.sidebar.slider("Demand B:", 0, 150, st.session_state.scenarios[selected]['demand_b'], 5, key=f"db_{selected}")
st.session_state.scenarios[selected]['profit_a'] = st.sidebar.slider("Profit A ($):", 50, 150, st.session_state.scenarios[selected]['profit_a'], 5, key=f"pa_{selected}")
st.session_state.scenarios[selected]['profit_b'] = st.sidebar.slider("Profit B ($):", 30, 100, st.session_state.scenarios[selected]['profit_b'], 5, key=f"pb_{selected}")

if st.sidebar.button("Reset All", use_container_width=True):
    st.session_state.scenarios = {
        'scenario1': {'name': 'Baseline', 'heat_treatment': 160, 'machining': 200, 'assembly': 180, 'demand_a': 50, 'demand_b': 80, 'profit_a': 90, 'profit_b': 60},
        'scenario2': {'name': 'Elevate Bottleneck', 'heat_treatment': 200, 'machining': 200, 'assembly': 180, 'demand_a': 50, 'demand_b': 80, 'profit_a': 90, 'profit_b': 60},
        'scenario3': {'name': 'Premium Product A', 'heat_treatment': 160, 'machining': 200, 'assembly': 180, 'demand_a': 50, 'demand_b': 80, 'profit_a': 140, 'profit_b': 60}
    }
    st.rerun()

# Solve all scenarios
results = {}
for sid, params in st.session_state.scenarios.items():
    results[sid], _ = create_goal_optimization_model(
        heat_treatment_capacity=params['heat_treatment'],
        machining_capacity=params['machining'],
        assembly_capacity=params['assembly'],
        demand_a=params['demand_a'],
        demand_b=params['demand_b'],
        profit_a=params['profit_a'],
        profit_b=params['profit_b']
    )
    results[sid]['name'] = params['name']

# Display scenarios
st.subheader("📊 Scenario Comparison")
cols = st.columns(3)

for idx, (sid, result) in enumerate(results.items()):
    with cols[idx]:
        is_best = result['total_throughput'] == max(r['total_throughput'] for r in results.values())
        badge = "👑 BEST" if is_best else ""
        border = "#16a34a" if is_best else "#94a3b8"
        
        st.markdown(f"""
        <div style="border: 3px solid {border}; border-radius: 8px; padding: 15px; background-color: #f8fafc;">
            <h3 style="color: #1e3a8a;">{result['name']} {badge}</h3>
            <div style="background-color: #dbeafe; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4 style="color: #1e40af;">Throughput: ${result['total_throughput']:,.2f}</h4>
            </div>
            <p style="color: #15803d;"><strong>Product A:</strong> {result['product_a']:.1f} units</p>
            <p style="color: #92400e;"><strong>Product B:</strong> {result['product_b']:.1f} units</p>
            <p style="color: #991b1b;"><strong>Bottleneck:</strong> {result['bottleneck']}</p>
        </div>
        """, unsafe_allow_html=True)

# Charts
st.subheader("📈 Visual Comparisons")
col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    names = [results[s]['name'] for s in ['scenario1', 'scenario2', 'scenario3']]
    throughputs = [results[s]['total_throughput'] for s in ['scenario1', 'scenario2', 'scenario3']]
    colors = ['#16a34a' if t == max(throughputs) else '#3b82f6' for t in throughputs]
    
    fig.add_trace(go.Bar(x=names, y=throughputs, marker_color=colors, text=[f'${t:,.0f}' for t in throughputs], textposition='outside'))
    fig.update_layout(title='Throughput Comparison', yaxis_title='Throughput ($)', showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = go.Figure()
    for sid in ['scenario1', 'scenario2', 'scenario3']:
        fig2.add_trace(go.Bar(name=results[sid]['name'], x=['Product A', 'Product B'], 
                             y=[results[sid]['product_a'], results[sid]['product_b']]))
    fig2.update_layout(title='Product Mix', yaxis_title='Units', barmode='group', height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Insights
st.subheader("💡 Automatic Insights")
best_sid = max(results.items(), key=lambda x: x[1]['total_throughput'])[0]
best = results[best_sid]
baseline = results['scenario1']['total_throughput']
improvement = best['total_throughput'] - baseline

st.success(f"**Best Scenario:** {best['name']} achieves ${best['total_throughput']:,.2f}")
if best_sid != 'scenario1':
    st.success(f"**Improvement:** ${improvement:,.2f} ({improvement/baseline*100:.1f}%) over baseline")

st.info("**Why Python > Excel:** Excel Solver requires 15+ minutes to manually solve, copy results, and create charts for 3 scenarios. Python does it all in 1 second!")
