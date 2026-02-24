import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="AI-Powered Startup Financial Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
<style>
.main-header {font-size: 2.5rem; font-weight: 700; color: #1f2937; margin-bottom: 2rem;}
.metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 12px; text-align:center;}
.kpi-metric {font-size: 2rem; font-weight: bold;}
.status-badge {padding: 0.5rem 1rem; border-radius: 25px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Database
# -------------------------------
DB_PATH = "startup_financials.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def create_db():
    conn = get_conn()
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

create_db()

# -------------------------------
# DB Functions
# -------------------------------
def save_project(user_id, project_name, data):
    conn = get_conn()
    cursor = conn.cursor()
    data_json = json.dumps(data)
    cursor.execute("SELECT id FROM projects WHERE user_id=? AND project_name=?", (user_id, project_name))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
            UPDATE projects
            SET data=?, updated_at=CURRENT_TIMESTAMP
            WHERE user_id=? AND project_name=?
        """, (data_json, user_id, project_name))
    else:
        cursor.execute("INSERT INTO projects (user_id, project_name, data) VALUES (?,?,?)",
                       (user_id, project_name, data_json))
    conn.commit()
    conn.close()

def load_project(user_id, project_name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM projects WHERE user_id=? AND project_name=? ORDER BY updated_at DESC LIMIT 1",
                   (user_id, project_name))
    result = cursor.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None

def load_all_projects(user_id):
    conn = get_conn()
    df = pd.read_sql_query("SELECT project_name FROM projects WHERE user_id=? ORDER BY updated_at DESC", conn,
                           params=(user_id,))
    conn.close()
    return df['project_name'].tolist() if not df.empty else []

def delete_project(user_id, project_name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE user_id=? AND project_name=?", (user_id, project_name))
    conn.commit()
    conn.close()

# -------------------------------
# Session State Init
# -------------------------------
if 'user_id' not in st.session_state:
    st.session_state.user_id = "default_user"  # لاحقًا يمكن استبداله ب auth system
if 'project_name' not in st.session_state:
    st.session_state.project_name = "Default Project"
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'auto_save' not in st.session_state:
    st.session_state.auto_save = True

user_id = st.session_state.user_id

# -------------------------------
# Sidebar - Project Management
# -------------------------------
st.sidebar.markdown("## 🏢 Project Management")

projects = load_all_projects(user_id)
selected = st.sidebar.selectbox("Select Project:", options=["New Project"] + projects, index=0)

# Create / Load / Delete without rerun
if selected == "New Project":
    new_name = st.sidebar.text_input("Project Name", value="My Startup")
    if st.sidebar.button("Create Project"):
        st.session_state.project_name = new_name
        st.session_state.data = {}
        save_project(user_id, new_name, st.session_state.data)
        st.success(f"✅ Project '{new_name}' created successfully!")
        projects = load_all_projects(user_id)

else:
    st.session_state.project_name = selected
    if st.sidebar.button("Load Project"):
        loaded = load_project(user_id, selected)
        if loaded:
            st.session_state.data = loaded
            st.success(f"✅ Project '{selected}' loaded successfully!")
        else:
            st.warning(f"⚠️ Project '{selected}' has no saved data yet.")

if st.sidebar.button("Delete Project"):
    delete_project(user_id, st.session_state.project_name)
    st.session_state.data = {}
    st.success(f"🗑️ Project '{st.session_state.project_name}' deleted successfully!")
    projects = load_all_projects(user_id)

st.sidebar.markdown("---")
st.sidebar.caption(f"💾 Auto-save: {'ON' if st.session_state.auto_save else 'OFF'}")

# -------------------------------
# Header
# -------------------------------
st.markdown('<h1 class="main-header">💰 AI-Powered Startup Financial Intelligence</h1>', unsafe_allow_html=True)
st.markdown("*Real-time unit economics • Break-even analysis • Pricing scenarios • Financial insights*")

# -------------------------------
# Load default data
# -------------------------------
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

# -------------------------------
# Input Form
# -------------------------------
with st.expander("📊 Input Financial Data", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💵 Unit Economics")
        data['material_cost'] = st.number_input("Material Cost ($/unit)", value=float(data.get('material_cost', 10.0)), step=0.1)
        data['packaging_cost'] = st.number_input("Packaging Cost ($/unit)", value=float(data.get('packaging_cost', 2.0)), step=0.1)
        data['shipping_cost'] = st.number_input("Shipping Cost ($/unit)", value=float(data.get('shipping_cost', 3.0)), step=0.1)
    with col2:
        st.markdown("### 🏭 Business Metrics")
        data['fixed_costs'] = st.number_input("Monthly Fixed Costs ($)", value=float(data.get('fixed_costs', 5000.0)), step=100)
        data['profit_margin'] = st.number_input("Target Profit Margin (%)", min_value=0.0, max_value=100.0, value=float(data.get('profit_margin', 30.0))*100, step=1)/100
        data['expected_sales'] = st.number_input("Expected Monthly Sales (units)", min_value=0, value=int(data.get('expected_sales', 1000)), step=100)

# -------------------------------
# Auto-save
# -------------------------------
if st.session_state.auto_save:
    save_project(user_id, st.session_state.project_name, data)

# -------------------------------
# Metrics Calculation
# -------------------------------
def calculate_metrics(data):
    total_variable = data['material_cost'] + data['packaging_cost'] + data['shipping_cost']
    selling_price = total_variable * (1 + data['profit_margin'])
    contribution_margin = selling_price - total_variable
    contribution_margin_pct = (contribution_margin / selling_price * 100) if selling_price else 0
    break_even_units = data['fixed_costs'] / contribution_margin if contribution_margin else float('inf')
    break_even_revenue = break_even_units * selling_price
    monthly_profit = (contribution_margin * data['expected_sales']) - data['fixed_costs']
    monthly_profit_margin = (monthly_profit / (selling_price * data['expected_sales']) * 100) if (selling_price*data['expected_sales']) else 0
    roi = (monthly_profit / data['fixed_costs'] * 100) if data['fixed_costs'] else 0
    return {
        'total_variable_cost': total_variable,
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

# -------------------------------
# Financial Health
# -------------------------------
def get_health_status(metrics):
    warnings = []
    if metrics['contribution_margin'] <= 0:
        return "🔴 CRITICAL", ["Negative contribution margin"]
    if metrics['contribution_margin_pct'] < 5:
        warnings.append("Low margin (<5%)")
    if metrics['break_even_units'] > data['expected_sales']*2:
        warnings.append("High break-even relative to sales")
    status = "🟢 HEALTHY" if not warnings else "🟡 MONITOR"
    return status, warnings

health_status, warnings = get_health_status(metrics)

# -------------------------------
# KPI Dashboard
# -------------------------------
st.markdown("### 📈 Financial KPIs")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Selling Price", f"${metrics['selling_price']:.2f}")
k2.metric("Contribution Margin", f"${metrics['contribution_margin']:.2f} ({metrics['contribution_margin_pct']:.1f}%)")
k3.metric("Break-even Units", f"{metrics['break_even_units']:.0f}")
profit_color = "🟢" if metrics['monthly_profit'] > 0 else "🔴"
k4.metric("Monthly Profit", f"{profit_color} ${metrics['monthly_profit']:,.0f}")

col1, col2 = st.columns([3,1])
with col1:
    st.markdown("### 🩺 Financial Health")
with col2:
    st.markdown(f'<span class="status-badge" style="background: {"#10b981" if "HEALTHY" in health_status else "#f59e0b" if "MONITOR" in health_status else "#ef4444"}; color:white">{health_status}</span>', unsafe_allow_html=True)

for w in warnings:
    st.warning(w)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("*Built with real financial principles • Auto-saves every change • Multi-user ready*")
st.caption(f"Last updated: {datetime.now()}")
