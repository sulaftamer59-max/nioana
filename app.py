import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------
# Page Config & Styling
# ---------------------------
st.set_page_config(
    page_title="AI-Powered Startup Financial System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {font-size: 2.5rem; font-weight: 700; color: #1f2937; margin-bottom: 2rem;}
.metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 12px; text-align:center;}
.kpi-metric {font-size: 2rem; font-weight: bold;}
.status-badge {padding: 0.5rem 1rem; border-radius: 25px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Database Helper
# ---------------------------
DB_PATH = "startup_financials.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def create_tables():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, project_name),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

create_tables()

# ---------------------------
# Session State Init
# ---------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "project_name" not in st.session_state:
    st.session_state.project_name = "Default Project"
if "data" not in st.session_state:
    st.session_state.data = {}
if "auto_save" not in st.session_state:
    st.session_state.auto_save = True

# ---------------------------
# User Login
# ---------------------------
st.sidebar.markdown("## 👤 User Login / Switch")
username_input = st.sidebar.text_input("Username", value="user1")
if st.sidebar.button("Login / Switch"):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username_input,))
    conn.commit()
    cursor.execute("SELECT id FROM users WHERE username=?", (username_input,))
    user_id = cursor.fetchone()[0]
    st.session_state.user_id = user_id
    conn.close()
    st.success(f"Logged in as: {username_input}")

# ---------------------------
# Database Operations
# ---------------------------
def save_project(user_id, project_name, data):
    conn = get_conn()
    cursor = conn.cursor()
    data_json = json.dumps(data)
    cursor.execute("""
        INSERT INTO projects (user_id, project_name, data)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, project_name)
        DO UPDATE SET data=excluded.data, updated_at=CURRENT_TIMESTAMP
    """, (user_id, project_name, data_json))
    conn.commit()
    conn.close()

def load_project(user_id, project_name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM projects WHERE user_id=? AND project_name=?", (user_id, project_name))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None

def load_all_projects(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT project_name FROM projects WHERE user_id=? ORDER BY updated_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows] if rows else []

def delete_project(user_id, project_name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE user_id=? AND project_name=?", (user_id, project_name))
    conn.commit()
    conn.close()

# ---------------------------
# Project Sidebar
# ---------------------------
if st.session_state.user_id:
    st.sidebar.markdown("## 🏢 Project Management")
    projects = load_all_projects(st.session_state.user_id)
    selected_project = st.sidebar.selectbox("Select Project:", options=["New Project"] + projects, index=0)

    if selected_project == "New Project":
        new_project_name = st.sidebar.text_input("New Project Name", value="My Startup")
        if st.sidebar.button("Create New Project"):
            st.session_state.project_name = new_project_name
            st.session_state.data = {
                'material_cost': 10.0, 'packaging_cost': 2.0, 'shipping_cost': 3.0,
                'fixed_costs': 5000.0, 'profit_margin': 0.3, 'expected_sales': 1000
            }
            save_project(st.session_state.user_id, st.session_state.project_name, st.session_state.data)
            st.experimental_rerun()
    else:
        st.session_state.project_name = selected_project
        if st.sidebar.button("Load Project"):
            loaded_data = load_project(st.session_state.user_id, selected_project)
            if loaded_data:
                st.session_state.data = loaded_data
                st.success(f"Loaded: {selected_project}")
                st.experimental_rerun()

        if st.sidebar.button("🗑️ Delete Project"):
            delete_project(st.session_state.user_id, selected_project)
            st.session_state.data = {}
            st.success("Project deleted!")
            st.experimental_rerun()

# ---------------------------
# Main Header
# ---------------------------
st.markdown('<h1 class="main-header">💰 AI-Powered Startup Financial Intelligence System</h1>', unsafe_allow_html=True)
st.markdown("*Real-time unit economics • Break-even analysis • Pricing scenarios • Financial health insights*")

# ---------------------------
# Load Data
# ---------------------------
if not st.session_state.data:
    st.session_state.data = {
        'material_cost': 10.0,
        'packaging_cost': 2.0,
        'shipping_cost': 3.0,
        'fixed_costs': 5000.0,
        'profit_margin': 0.3,
        'expected_sales': 1000
    }

data = st.session_state.data

# ---------------------------
# Input Form
# ---------------------------
with st.expander("📊 Input Financial Data", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💵 Unit Economics")
        data['material_cost'] = st.number_input("Material Cost ($/unit)", min_value=0.0, value=float(data['material_cost']), step=0.1)
        data['packaging_cost'] = st.number_input("Packaging Cost ($/unit)", min_value=0.0, value=float(data['packaging_cost']), step=0.1)
        data['shipping_cost'] = st.number_input("Shipping Cost ($/unit)", min_value=0.0, value=float(data['shipping_cost']), step=0.1)
    with col2:
        st.markdown("### 🏭 Business Metrics")
        data['fixed_costs'] = st.number_input("Monthly Fixed Costs ($)", min_value=0.0, value=float(data['fixed_costs']), step=100.0)
        data['profit_margin'] = st.number_input("Target Profit Margin (%)", min_value=0.0, max_value=100.0, value=float(data['profit_margin']*100), step=1.0)/100
        data['expected_sales'] = st.number_input("Expected Monthly Sales (units)", min_value=0, value=int(data['expected_sales']), step=100)

# ---------------------------
# Auto-save
# ---------------------------
if st.session_state.auto_save and st.session_state.user_id:
    save_project(st.session_state.user_id, st.session_state.project_name, data)

# ---------------------------
# Financial Calculations
# ---------------------------
def calculate_metrics(data):
    total_variable_cost = data['material_cost'] + data['packaging_cost'] + data['shipping_cost']
    selling_price = total_variable_cost * (1 + data['profit_margin'])
    contribution_margin = selling_price - total_variable_cost
    contribution_margin_pct = (contribution_margin / selling_price) * 100 if selling_price > 0 else 0
    break_even_units = data['fixed_costs'] / contribution_margin if contribution_margin > 0 else float('inf')
    break_even_revenue = break_even_units * selling_price
    monthly_profit = (contribution_margin * data['expected_sales']) - data['fixed_costs']
    monthly_profit_margin = (monthly_profit / (selling_price * data['expected_sales'])) * 100 if (selling_price * data['expected_sales'])>0 else 0
    roi = (monthly_profit / data['fixed_costs'] * 100) if data['fixed_costs']>0 else 0
    return {
        'total_variable_cost': total_variable_cost,
        'selling_price': selling_price,
        'contribution_margin': contribution_margin,
        'contribution_margin_pct': contribution_margin_pct,
        'break_even_units': break_even_units,
        'break_even_revenue': break_even_revenue,
        'monthly_profit': monthly_profit,
        'monthly_profit_margin': monthly_profit_margin,
        'roi': roi
    }

metrics = calculate_metrics(data)

# ---------------------------
# KPI Dashboard
# ---------------------------
st.markdown("### 📈 Financial KPIs")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Selling Price", f"${metrics['selling_price']:.2f}")
c2.metric("Contribution Margin", f"${metrics['contribution_margin']:.2f} ({metrics['contribution_margin_pct']:.1f}%)")
c3.metric("Break-even Units", f"{metrics['break_even_units']:.0f}")
c4.metric("Monthly Profit", f"${metrics['monthly_profit']:.0f}")

# ---------------------------
# Charts (Profit & Break-even)
# ---------------------------
st.markdown("### 📊 Analytics")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    prices = np.linspace(metrics['total_variable_cost']*0.8, metrics['total_variable_cost']*2, 100)
    profits = (prices - metrics['total_variable_cost']) * data['expected_sales'] - data['fixed_costs']
    fig_profit = px.line(x=prices, y=profits, labels={'x':'Price ($)','y':'Profit ($)'}, title="Profit vs Price")
    fig_profit.add_hline(y=0, line_dash="dash", line_color="red")
    fig_profit.add_vline(x=metrics['selling_price'], line_dash="dot", line_color="green", annotation_text="Current Price")
    st.plotly_chart(fig_profit, use_container_width=True)

with col_chart2:
    x_units = np.arange(0, data['expected_sales']*1.5, 50)
    revenue = x_units * metrics['selling_price']
    total_cost = (x_units * metrics['total_variable_cost']) + data['fixed_costs']
    profit = revenue - total_cost
    fig_be = make_subplots(specs=[[{"secondary_y": True}]])
    fig_be.add_trace(go.Scatter(x=x_units, y=revenue, name="Revenue", line=dict(color='green')), secondary_y=False)
    fig_be.add_trace(go.Scatter(x=x_units, y=total_cost, name="Total Cost", line=dict(color='red')), secondary_y=False)
    fig_be.add_trace(go.Scatter(x=x_units, y=profit, name="Profit", line=dict(color='blue')), secondary_y=True)
    fig_be.add_vline(x=metrics['break_even_units'], line_dash="dash", line_color="orange", annotation_text=f"Break-even")
    fig_be.add_vline(x=data['expected_sales'], line_dash="dot", line_color="purple", annotation_text=f"Expected Sales")
    fig_be.update_layout(title="Break-even Analysis", height=400)
    st.plotly_chart(fig_be, use_container_width=True)

# ---------------------------
# Export
# ---------------------------
st.markdown("---")
export_data = {**data, **metrics}
csv = pd.DataFrame([export_data]).to_csv(index=False)
st.download_button("📤 Export CSV", csv, f"{st.session_state.project_name}_financials.csv")
