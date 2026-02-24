# app.py

import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ========================
# 1️⃣ Streamlit Page Config
# ========================
st.set_page_config(
    page_title="AI-Powered Startup Financial System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# 2️⃣ Supabase Auth Setup
# ========================
# تحتاجي تنشئي حساب Supabase وتحطي URL و API KEY
SUPABASE_URL = "https://xyzcompany.supabase.co"
SUPABASE_KEY = "public-anon-key"

from supabase import create_client, Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# تسجيل الدخول أو تسجيل مستخدم جديد
st.sidebar.markdown("## 🔐 User Authentication")
auth_option = st.sidebar.radio("Choose:", ["Login", "Sign Up"])

if auth_option == "Sign Up":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Sign Up"):
        user = supabase.auth.sign_up({"email": email, "password": password})
        st.success("User signed up! Please log in.")
        st.stop()

else:  # Login
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = supabase.auth.sign_in({"email": email, "password": password})
        if user.user:
            st.session_state.user_id = user.user.id
            st.success(f"Logged in as {email}")
        else:
            st.error("Login failed")
            st.stop()

user_id = st.session_state.get("user_id", None)
if not user_id:
    st.stop()

# ========================
# 3️⃣ Database Functions (Supabase)
# ========================
def save_project(project_name, data):
    """Save or update project for current user"""
    data_json = json.dumps(data)
    existing = supabase.table("projects").select("*").eq("user_id", user_id).eq("project_name", project_name).execute()
    if existing.data:
        supabase.table("projects").update({"data": data_json, "updated_at": datetime.now().isoformat()}).eq("user_id", user_id).eq("project_name", project_name).execute()
    else:
        supabase.table("projects").insert({"user_id": user_id, "project_name": project_name, "data": data_json}).execute()

def load_project(project_name):
    """Load project for current user"""
    res = supabase.table("projects").select("data").eq("user_id", user_id).eq("project_name", project_name).execute()
    if res.data:
        return json.loads(res.data[0]["data"])
    return None

def load_all_projects():
    """List all projects for current user"""
    res = supabase.table("projects").select("project_name").eq("user_id", user_id).execute()
    return [p["project_name"] for p in res.data]

def delete_project(project_name):
    supabase.table("projects").delete().eq("user_id", user_id).eq("project_name", project_name).execute()

# ========================
# 4️⃣ Project Management Sidebar
# ========================
st.sidebar.markdown("## 🏢 Project Management")
projects = load_all_projects()
selected_project = st.sidebar.selectbox(
    "Select Project",
    options=["New Project"] + projects
)

if selected_project == "New Project":
    new_project_name = st.sidebar.text_input("New Project Name", value="My Startup")
    if st.sidebar.button("Create New Project"):
        st.session_state.project_name = new_project_name
        st.session_state.data = {}
        st.experimental_rerun()
else:
    st.session_state.project_name = selected_project
    if st.sidebar.button("Load Project"):
        st.session_state.data = load_project(selected_project) or {}
        st.success(f"Loaded: {selected_project}")
        st.experimental_rerun()

if st.sidebar.button("🗑️ Delete Project"):
    delete_project(st.session_state.project_name)
    st.session_state.data = {}
    st.success("Deleted!")
    st.experimental_rerun()

# ========================
# 5️⃣ Default Financial Data
# ========================
data = st.session_state.get("data", {})
if not data:
    data = {
        "material_cost": 10.0,
        "packaging_cost": 2.0,
        "shipping_cost": 3.0,
        "fixed_costs": 5000.0,
        "profit_margin": 0.3,
        "expected_sales": 1000,
        "projected_growth": 0.1
    }

# ========================
# 6️⃣ Input Form
# ========================
with st.expander("📊 Input Financial Data", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        data["material_cost"] = st.number_input("Material Cost ($/unit)", value=data["material_cost"])
        data["packaging_cost"] = st.number_input("Packaging Cost ($/unit)", value=data["packaging_cost"])
        data["shipping_cost"] = st.number_input("Shipping Cost ($/unit)", value=data["shipping_cost"])
    with col2:
        data["fixed_costs"] = st.number_input("Monthly Fixed Costs ($)", value=data["fixed_costs"])
        data["profit_margin"] = st.number_input("Target Profit Margin (%)", value=data["profit_margin"]*100)/100
        data["expected_sales"] = st.number_input("Expected Monthly Sales (units)", value=data["expected_sales"])

# ========================
# 7️⃣ Auto-Save
# ========================
save_project(st.session_state.project_name, data)

# ========================
# 8️⃣ Metrics Calculation
# ========================
def calculate_metrics(data):
    total_variable_cost = data["material_cost"] + data["packaging_cost"] + data["shipping_cost"]
    selling_price = total_variable_cost * (1 + data["profit_margin"])
    contribution_margin = selling_price - total_variable_cost
    contribution_margin_pct = (contribution_margin / selling_price) * 100 if selling_price else 0
    break_even_units = data["fixed_costs"] / contribution_margin if contribution_margin > 0 else float("inf")
    break_even_revenue = break_even_units * selling_price
    monthly_profit = (contribution_margin * data["expected_sales"]) - data["fixed_costs"]
    monthly_profit_margin = (monthly_profit / (selling_price*data["expected_sales"]))*100 if selling_price*data["expected_sales"] else 0
    roi = (monthly_profit / data["fixed_costs"])*100 if data["fixed_costs"] else 0
    return {
        "total_variable_cost": total_variable_cost,
        "selling_price": selling_price,
        "contribution_margin": contribution_margin,
        "contribution_margin_pct": contribution_margin_pct,
        "break_even_units": break_even_units,
        "break_even_revenue": break_even_revenue,
        "monthly_profit": monthly_profit,
        "monthly_profit_margin": monthly_profit_margin,
        "roi": roi
    }

metrics = calculate_metrics(data)

# ========================
# 9️⃣ KPI Dashboard
# ========================
st.markdown("### 📈 Financial KPIs")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Selling Price", f"${metrics['selling_price']:.2f}")
col2.metric("Contribution Margin", f"${metrics['contribution_margin']:.2f}", f"{metrics['contribution_margin_pct']:.1f}%")
col3.metric("Break-even Units", f"{metrics['break_even_units']:.0f}")
col4.metric("Monthly Profit", f"${metrics['monthly_profit']:.0f}")

# ========================
# 10️⃣ Charts
# ========================
# Profit vs Price
prices = np.linspace(metrics["total_variable_cost"]*0.8, metrics["total_variable_cost"]*2, 100)
profits = (prices - metrics["total_variable_cost"])*data["expected_sales"] - data["fixed_costs"]
fig = px.line(x=prices, y=profits, labels={"x":"Selling Price ($)","y":"Monthly Profit ($)"}, title="Profit vs Price")
fig.add_hline(y=0, line_dash="dash", line_color="red")
st.plotly_chart(fig, use_container_width=True)

# Break-even Chart
x_units = np.arange(0, data["expected_sales"]*1.5, 50)
revenue = x_units * metrics["selling_price"]
total_cost = (x_units*metrics["total_variable_cost"])+data["fixed_costs"]
profit = revenue - total_cost
fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(go.Scatter(x=x_units, y=revenue, name="Revenue"), secondary_y=False)
fig2.add_trace(go.Scatter(x=x_units, y=total_cost, name="Total Cost"), secondary_y=False)
fig2.add_trace(go.Scatter(x=x_units, y=profit, name="Profit"), secondary_y=True)
st.plotly_chart(fig2, use_container_width=True)

# ========================
# 11️⃣ Scenario Modeling
# ========================
scenarios = {
    "Conservative":{"sales":data["expected_sales"]*0.7,"margin":data["profit_margin"]*0.9},
    "Expected":{"sales":data["expected_sales"],"margin":data["profit_margin"]},
    "Aggressive":{"sales":data["expected_sales"]*1.3,"margin":data["profit_margin"]*1.1}
}

scenario_data = []
for name, params in scenarios.items():
    temp = data.copy()
    temp["expected_sales"] = params["sales"]
    temp["profit_margin"] = params["margin"]
    m = calculate_metrics(temp)
    scenario_data.append({
        "Scenario":name,
        "Sales":f"{params['sales']:.0f}",
        "Price":f"${m['selling_price']:.1f}",
        "Profit":f"${m['monthly_profit']:.0f}",
        "Margin":f"{m['contribution_margin_pct']:.1f}%"
    })
st.dataframe(pd.DataFrame(scenario_data))

# ========================
# 12️⃣ Export CSV
# ========================
export_data = {**data, **metrics}
csv = pd.DataFrame([export_data]).to_csv(index=False)
st.download_button("📤 Export CSV", csv, f"{st.session_state.project_name}_financials.csv")
