# app.py
import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import hashlib

# ----------------------
# Page config
# ----------------------
st.set_page_config(
    page_title="AI Startup Financial System",
    page_icon="💰",
    layout="wide"
)

# ----------------------
# Database Setup
# ----------------------
DB_PATH = "multiuser_financials.db"

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        project_name TEXT NOT NULL,
        data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, project_name)
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ----------------------
# Helper Functions
# ----------------------
def get_user_id(username: str):
    return hashlib.sha256(username.encode()).hexdigest()

def save_project(user_id, project_name, data):
    data_json = json.dumps(data)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM projects WHERE user_id=? AND project_name=?", (user_id, project_name))
    if cursor.fetchone():
        cursor.execute("UPDATE projects SET data=?, updated_at=CURRENT_TIMESTAMP WHERE user_id=? AND project_name=?", (data_json, user_id, project_name))
    else:
        cursor.execute("INSERT INTO projects (user_id, project_name, data) VALUES (?, ?, ?)", (user_id, project_name, data_json))
    conn.commit()
    conn.close()

def load_project(user_id, project_name):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM projects WHERE user_id=? AND project_name=?", (user_id, project_name))
    res = cursor.fetchone()
    conn.close()
    if res:
        return json.loads(res[0])
    return None

def load_all_projects(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT project_name FROM projects WHERE user_id=? ORDER BY updated_at DESC", (user_id,))
    res = cursor.fetchall()
    conn.close()
    return [r[0] for r in res]

def delete_project(user_id, project_name):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE user_id=? AND project_name=?", (user_id, project_name))
    conn.commit()
    conn.close()

# ----------------------
# User Login
# ----------------------
st.sidebar.markdown("## 🔑 User Login / Sign-in")
username = st.sidebar.text_input("Enter your username")
if username:
    user_id = get_user_id(username)
else:
    st.warning("Please enter a username to continue.")
    st.stop()

# ----------------------
# Session State Initialization
# ----------------------
if "project_name" not in st.session_state:
    st.session_state.project_name = "New Project"
if "data" not in st.session_state:
    st.session_state.data = {}

# ----------------------
# Sidebar - Project Management
# ----------------------
st.sidebar.markdown("## 🏢 Project Management")
projects = load_all_projects(user_id)
selected = st.sidebar.selectbox("Select Project", ["New Project"] + projects)

if selected == "New Project":
    new_name = st.sidebar.text_input("Project Name", value="My Startup")
    if st.sidebar.button("Create Project"):
        st.session_state.project_name = new_name
        st.session_state.data = {}
        save_project(user_id, new_name, st.session_state.data)
        st.experimental_rerun()
else:
    st.session_state.project_name = selected
    if st.sidebar.button("Load Project"):
        st.session_state.data = load_project(user_id, selected) or {}
        st.success(f"Loaded {selected}")
        st.experimental_rerun()

if st.sidebar.button("Delete Project"):
    delete_project(user_id, st.session_state.project_name)
    st.session_state.data = {}
    st.success("Project deleted!")
    st.experimental_rerun()

# ----------------------
# Default Financial Data
# ----------------------
data = st.session_state.data
if not data:
    data = {
        "material_cost": 10.0,
        "packaging_cost": 2.0,
        "shipping_cost": 3.0,
        "fixed_costs": 5000.0,
        "profit_margin": 0.3,
        "expected_sales": 1000
    }

# ----------------------
# Input Form
# ----------------------
with st.expander("📊 Input Financial Data", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        data["material_cost"] = st.number_input("Material Cost ($/unit)", value=data["material_cost"])
        data["packaging_cost"] = st.number_input("Packaging Cost ($/unit)", value=data["packaging_cost"])
        data["shipping_cost"] = st.number_input("Shipping Cost ($/unit)", value=data["shipping_cost"])
    with col2:
        data["fixed_costs"] = st.number_input("Monthly Fixed Costs ($)", value=data["fixed_costs"])
        data["profit_margin"] = st.number_input("Target Profit Margin (%)", value=data["profit_margin"]*100)/100
        data["expected_sales"] = st.number_input("Expected Monthly Sales", value=data["expected_sales"])

# ----------------------
# Auto-save for multi-user
# ----------------------
save_project(user_id, st.session_state.project_name, data)

# ----------------------
# Metrics Calculation
# ----------------------
def calculate_metrics(d):
    total_var = d["material_cost"] + d["packaging_cost"] + d["shipping_cost"]
    selling_price = total_var * (1 + d["profit_margin"])
    contribution = selling_price - total_var
    contribution_pct = (contribution / selling_price * 100) if selling_price else 0
    break_even = d["fixed_costs"] / contribution if contribution else float("inf")
    profit = contribution * d["expected_sales"] - d["fixed_costs"]
    roi = (profit / d["fixed_costs"]*100) if d["fixed_costs"] else 0
    return {
        "total_variable_cost": total_var,
        "selling_price": selling_price,
        "contribution_margin": contribution,
        "contribution_margin_pct": contribution_pct,
        "break_even_units": break_even,
        "monthly_profit": profit,
        "roi": roi
    }

metrics = calculate_metrics(data)

# ----------------------
# KPI Dashboard
# ----------------------
st.markdown(f"### 💰 Dashboard for {username} / {st.session_state.project_name}")
c1,c2,c3,c4 = st.columns(4)
c1.metric("Selling Price", f"${metrics['selling_price']:.2f}")
c2.metric("Contribution Margin", f"${metrics['contribution_margin']:.2f}", f"{metrics['contribution_margin_pct']:.1f}%")
c3.metric("Break-even Units", f"{metrics['break_even_units']:.0f}")
c4.metric("Monthly Profit", f"${metrics['monthly_profit']:.0f}")

# ----------------------
# Charts
# ----------------------
prices = np.linspace(metrics["total_variable_cost"]*0.8, metrics["total_variable_cost"]*2, 100)
profits = (prices - metrics["total_variable_cost"])*data["expected_sales"] - data["fixed_costs"]
fig = px.line(x=prices, y=profits, labels={"x":"Selling Price","y":"Monthly Profit"}, title="Profit vs Price")
fig.add_hline(y=0,line_dash="dash",line_color="red")
st.plotly_chart(fig,use_container_width=True)

x_units = np.arange(0,data["expected_sales"]*1.5,50)
revenue = x_units*metrics["selling_price"]
total_cost = x_units*metrics["total_variable_cost"] + data["fixed_costs"]
profit = revenue - total_cost
fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(go.Scatter(x=x_units,y=revenue,name="Revenue"),secondary_y=False)
fig2.add_trace(go.Scatter(x=x_units,y=total_cost,name="Total Cost"),secondary_y=False)
fig2.add_trace(go.Scatter(x=x_units,y=profit,name="Profit"),secondary_y=True)
st.plotly_chart(fig2,use_container_width=True)

# ----------------------
# Scenario Modeling
# ----------------------
scenarios = {
    "Conservative":{"sales":data["expected_sales"]*0.7,"margin":data["profit_margin"]*0.9},
    "Expected":{"sales":data["expected_sales"],"margin":data["profit_margin"]},
    "Aggressive":{"sales":data["expected_sales"]*1.3,"margin":data["profit_margin"]*1.1}
}
scenario_data = []
for name,params in scenarios.items():
    temp = data.copy()
    temp["expected_sales"] = params["sales"]
    temp["profit_margin"] = params["margin"]
    m = calculate_metrics(temp)
    scenario_data.append({
        "Scenario": name,
        "Sales": f"{params['sales']:.0f}",
        "Price": f"${m['selling_price']:.2f}",
        "Profit": f"${m['monthly_profit']:.0f}",
        "Margin": f"{m['contribution_margin_pct']:.1f}%"
    })
st.dataframe(pd.DataFrame(scenario_data))
