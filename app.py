import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import json
from datetime import datetime
import plotly.express as px

# -------------------------------
# Config
# -------------------------------
st.set_page_config(
    page_title="AI Startup Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Database setup
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
# DB functions
# -------------------------------
def save_project(user_id, project_name, data):
    conn = get_conn()
    cursor = conn.cursor()
    data_json = json.dumps(data)
    cursor.execute("SELECT id FROM projects WHERE user_id=? AND project_name=?", (user_id, project_name))
    if cursor.fetchone():
        cursor.execute("""
            UPDATE projects SET data=?, updated_at=CURRENT_TIMESTAMP
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
# Session State
# -------------------------------
if 'user_id' not in st.session_state:
    st.session_state.user_id = "user_default"
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
selected_project = st.sidebar.selectbox("Select Project:", options=["New Project"] + projects, index=0)

# Create project
if selected_project == "New Project":
    new_name = st.sidebar.text_input("Project Name", value="My Startup")
    if st.sidebar.button("Create Project"):
        st.session_state.project_name = new_name
        st.session_state.data = {
            'material_cost':10, 'packaging_cost':2, 'shipping_cost':3,
            'fixed_costs':5000, 'profit_margin':0.3, 'expected_sales':1000
        }
        save_project(user_id, new_name, st.session_state.data)
        st.success(f"✅ Project '{new_name}' created!")

# Load project
else:
    st.session_state.project_name = selected_project
    if st.sidebar.button("Load Project"):
        loaded = load_project(user_id, selected_project)
        if loaded:
            st.session_state.data = loaded
            st.success(f"✅ Project '{selected_project}' loaded!")

# Delete project
if st.sidebar.button("Delete Project"):
    delete_project(user_id, st.session_state.project_name)
    st.session_state.data = {}
    st.success(f"🗑️ Project '{st.session_state.project_name}' deleted!")

st.sidebar.caption(f"💾 Auto-save: {'ON' if st.session_state.auto_save else 'OFF'}")

# -------------------------------
# Main UI
# -------------------------------
st.markdown("# 💰 AI Startup Finance Dashboard")
st.markdown("*Unit economics • Break-even • Pricing • Profit analysis*")

# Default data
if not st.session_state.data:
    st.session_state.data = {
        'material_cost':10, 'packaging_cost':2, 'shipping_cost':3,
        'fixed_costs':5000, 'profit_margin':0.3, 'expected_sales':1000
    }

data = st.session_state.data

# Input form
with st.expander("📊 Input Financial Data", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        data['material_cost'] = st.number_input("Material Cost ($/unit)", value=float(data.get('material_cost',10)), step=0.1)
        data['packaging_cost'] = st.number_input("Packaging Cost ($/unit)", value=float(data.get('packaging_cost',2)), step=0.1)
        data['shipping_cost'] = st.number_input("Shipping Cost ($/unit)", value=float(data.get('shipping_cost',3)), step=0.1)
    with col2:
        data['fixed_costs'] = st.number_input("Monthly Fixed Costs ($)", value=float(data.get('fixed_costs',5000)), step=100)
        data['profit_margin'] = st.number_input("Profit Margin (%)", min_value=0.0, max_value=100.0, value=float(data.get('profit_margin',0.3)*100), step=1)/100
        data['expected_sales'] = st.number_input("Expected Monthly Sales", min_value=0, value=int(data.get('expected_sales',1000)), step=100)

# Auto-save
if st.session_state.auto_save:
    save_project(user_id, st.session_state.project_name, data)

# Metrics calculation
def calc_metrics(d):
    total_var = d['material_cost'] + d['packaging_cost'] + d['shipping_cost']
    sell_price = total_var*(1+d['profit_margin'])
    cont_margin = sell_price - total_var
    cont_pct = cont_margin/sell_price*100 if sell_price>0 else 0
    breakeven_units = d['fixed_costs']/cont_margin if cont_margin>0 else float('inf')
    breakeven_rev = breakeven_units*sell_price
    monthly_profit = cont_margin*d['expected_sales'] - d['fixed_costs']
    monthly_profit_pct = monthly_profit/(sell_price*d['expected_sales'])*100 if sell_price*d['expected_sales']>0 else 0
    roi = monthly_profit/d['fixed_costs']*100 if d['fixed_costs']>0 else 0
    return {
        'total_variable_cost':total_var, 'selling_price':sell_price,
        'contribution_margin':cont_margin, 'contribution_margin_pct':cont_pct,
        'break_even_units':breakeven_units, 'break_even_revenue':breakeven_rev,
        'monthly_profit':monthly_profit, 'monthly_profit_margin':monthly_profit_pct,
        'roi':roi
    }

metrics = calc_metrics(data)

# KPI display
st.markdown("### 📈 Financial KPIs")
c1,c2,c3,c4 = st.columns(4)
c1.metric("Selling Price", f"${metrics['selling_price']:.2f}")
c2.metric("Contribution Margin", f"${metrics['contribution_margin']:.2f} ({metrics['contribution_margin_pct']:.1f}%)")
c3.metric("Break-even Units", f"{metrics['break_even_units']:.0f}")
profit_color = "🟢" if metrics['monthly_profit']>0 else "🔴"
c4.metric("Monthly Profit", f"{profit_color} ${metrics['monthly_profit']:,.0f}")

# -------------------------------
# Requirements for plotting and exporting if needed
# -------------------------------
st.markdown("---")
st.caption(f"Last updated: {datetime.now()}")
