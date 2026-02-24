import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config for premium SaaS look
st.set_page_config(
    page_title="AI-Powered Startup Financial Intelligence System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: 700; color: #1f2937; margin-bottom: 2rem;}
    .metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 12px;}
    .kpi-metric {font-size: 2rem; font-weight: bold;}
    .status-badge {padding: 0.5rem 1rem; border-radius: 25px; font-weight: 600;}
    </style>
""", unsafe_allow_html=True)

class FinancialIntelligenceSystem:
    def __init__(self):
        self.db_path = "startup_financials.db"
        self.create_database()
        
    def create_database(self):
        """Initialize SQLite database with projects table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def save_project(self, project_name, data):
        """Save or update project data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if project exists
        cursor.execute("SELECT id FROM projects WHERE project_name = ?", (project_name,))
        existing = cursor.fetchone()
        
        data_json = json.dumps(data)
        if existing:
            cursor.execute("""
                UPDATE projects 
                SET data = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE project_name = ?
            """, (data_json, project_name))
        else:
            cursor.execute("""
                INSERT INTO projects (project_name, data) 
                VALUES (?, ?)
            """, (project_name, data_json))
        
        conn.commit()
        conn.close()
    
    def load_project(self, project_name):
        """Load project data by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT data FROM projects 
            WHERE project_name = ? 
            ORDER BY updated_at DESC LIMIT 1
        """, (project_name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def load_all_projects(self):
        """Load all project names for sidebar"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT project_name FROM projects ORDER BY updated_at DESC", conn)
        conn.close()
        return df['project_name'].tolist() if not df.empty else []
    
    def delete_project(self, project_name):
        """Delete a project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE project_name = ?", (project_name,))
        conn.commit()
        conn.close()

# Initialize session state
if 'system' not in st.session_state:
    st.session_state.system = FinancialIntelligenceSystem()
    st.session_state.project_name = "Default Project"
    st.session_state.data = {}
    st.session_state.auto_save = True

system = st.session_state.system

# Sidebar - Project Management
with st.sidebar:
    st.markdown("## 🏢 Project Management")
    
    # Project selector
    projects = system.load_all_projects()
    selected_project = st.selectbox(
        "Select Project:",
        options=["New Project"] + projects,
        index=0 if "New Project" in ["New Project"] + projects else None
    )
    
    if selected_project == "New Project":
        new_project_name = st.text_input("New Project Name", value="My Startup")
        if st.button("Create New Project", use_container_width=True):
            st.session_state.project_name = new_project_name
            st.session_state.data = {}
            st.rerun()
    else:
        st.session_state.project_name = selected_project
        
        if st.button("Load Project", use_container_width=True):
            loaded_data = system.load_project(selected_project)
            if loaded_data:
                st.session_state.data = loaded_data
                st.success(f"Loaded: {selected_project}")
                st.rerun()
    
    # Delete project
    if st.button("🗑️ Delete Current Project", type="secondary"):
        system.delete_project(st.session_state.project_name)
        st.session_state.data = {}
        st.success("Project deleted!")
        st.rerun()
    
    st.markdown("---")
    st.caption(f"💾 Auto-save: {'ON' if st.session_state.auto_save else 'OFF'}")

# Main Header
st.markdown('<h1 class="main-header">💰 AI-Powered Startup Financial Intelligence System</h1>', unsafe_allow_html=True)
st.markdown("*Real-time unit economics • Break-even analysis • Pricing scenarios • Financial health insights*")

# Load data on startup
if not st.session_state.data:
    default_data = {
        'material_cost': 10.0,
        'packaging_cost': 2.0,
        'shipping_cost': 3.0,
        'fixed_costs': 5000.0,
        'profit_margin': 0.3,
        'expected_sales': 1000,
        'projected_growth': 0.1
    }
    loaded_data = system.load_project(st.session_state.project_name)
    st.session_state.data = loaded_data or default_data

# Data input form
data = st.session_state.data

with st.expander("📊 Input Financial Data", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💵 Unit Economics")
        data['material_cost'] = st.number_input("Material Cost ($/unit)", min_value=0.0, value=float(data.get('material_cost', 10.0)), step=0.1)
        data['packaging_cost'] = st.number_input("Packaging Cost ($/unit)", min_value=0.0, value=float(data.get('packaging_cost', 2.0)), step=0.1)
        data['shipping_cost'] = st.number_input("Shipping Cost ($/unit)", min_value=0.0, value=float(data.get('shipping_cost', 3.0)), step=0.1)
    
    with col2:
        st.markdown("### 🏭 Business Metrics")
        data['fixed_costs'] = st.number_input("Monthly Fixed Costs ($)", min_value=0.0, value=float(data.get('fixed_costs', 5000.0)), step=100.0)
        data['profit_margin'] = st.number_input("Target Profit Margin (%)", min_value=0.0, max_value=100.0, value=float(data.get('profit_margin', 30.0)), step=1.0) / 100
        data['expected_sales'] = st.number_input("Expected Monthly Sales (units)", min_value=0, value=int(data.get('expected_sales', 1000)), step=100)

# Auto-save on change
if st.session_state.auto_save:
    system.save_project(st.session_state.project_name, data)

# Calculate metrics
@st.cache_data
def calculate_metrics(data):
    """Core financial calculations using real business formulas"""
    
    # Unit Economics
    total_variable_cost = data['material_cost'] + data['packaging_cost'] + data['shipping_cost']
    selling_price = total_variable_cost * (1 + data['profit_margin'])
    contribution_margin = selling_price - total_variable_cost
    contribution_margin_pct = (contribution_margin / selling_price) * 100 if selling_price > 0 else 0
    
    # Break-even Analysis
    break_even_units = data['fixed_costs'] / contribution_margin if contribution_margin > 0 else float('inf')
    break_even_revenue = break_even_units * selling_price
    
    # Monthly Profit
    monthly_profit = (contribution_margin * data['expected_sales']) - data['fixed_costs']
    monthly_profit_margin = (monthly_profit / (selling_price * data['expected_sales'])) * 100 if (selling_price * data['expected_sales']) > 0 else 0
    
    # ROI
    roi = ((monthly_profit / data['fixed_costs']) * 100) if data['fixed_costs'] > 0 else 0
    
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

# Financial Health Status
def get_health_status(metrics):
    """Determine financial health based on key indicators"""
    warnings = []
    
    if metrics['contribution_margin'] <= 0:
        return "🔴 CRITICAL", ["Negative contribution margin - business not viable"]
    if metrics['contribution_margin_pct'] < 5:
        return "🟡 CAUTION", ["Low margin (<5%) - high risk"]
    if metrics['contribution_margin_pct'] > 80:
        warnings.append("Very high margin (>80%) - verify assumptions")
    if metrics['break_even_units'] > data['expected_sales'] * 2:
        warnings.append("High break-even relative to sales")
    
    status = "🟢 HEALTHY" if not warnings else "🟡 MONITOR"
    return status, warnings

health_status, warnings = get_health_status(metrics)

# KPI Dashboard
st.markdown("### 📈 Financial KPIs")
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div>${metrics['selling_price']:.2f}</div>
        <div style='font-size: 0.9rem;'>Selling Price</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    delta = f"{metrics['contribution_margin_pct']:.1f}%"
    st.markdown(f"""
    <div class="metric-card">
        <div>${metrics['contribution_margin']:.2f}</div>
        <div style='font-size: 0.9rem;'>{delta}<br>Contribution Margin</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="metric-card">
        <div>{metrics['break_even_units']:.0f}</div>
        <div style='font-size: 0.9rem;'>Break-even Units</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    color = "🟢" if metrics['monthly_profit'] > 0 else "🔴"
    st.markdown(f"""
    <div class="metric-card">
        <div>{color} ${metrics['monthly_profit']:,.0f}</div>
        <div style='font-size: 0.9rem;'>Monthly Profit</div>
    </div>
    """, unsafe_allow_html=True)

# Health Status Badge
col1, col2 = st.columns([3,1])
with col1:
    st.markdown("### 🩺 Financial Health")
with col2:
    st.markdown(f'<span class="status-badge" style="background: {"#10b981" if "HEALTHY" in health_status else "#f59e0b" if "MONITOR" in health_status else "#ef4444"}; color: white; float: right;">{health_status}</span>', unsafe_allow_html=True)

if warnings:
    for warning in warnings:
        st.warning(warning)

# Charts Section
st.markdown("### 📊 Advanced Analytics")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Profit vs Price Curve
    prices = np.linspace(metrics['total_variable_cost'] * 0.8, metrics['total_variable_cost'] * 2, 100)
    profits = (prices - metrics['total_variable_cost']) * data['expected_sales'] - data['fixed_costs']
    
    fig_profit = px.line(
        x=prices, y=profits,
        title="Profit vs Price Sensitivity",
        labels={'x': 'Selling Price ($)', 'y': 'Monthly Profit ($)'}
    )
    fig_profit.add_hline(y=0, line_dash="dash", line_color="red")
    fig_profit.add_vline(x=metrics['selling_price'], line_dash="dot", line_color="green", annotation_text="Current Price")
    st.plotly_chart(fig_profit, use_container_width=True)

with chart_col2:
    # Break-even Visualization
    fig_be = make_subplots(specs=[[{"secondary_y": True}]])
    
    x_units = np.arange(0, data['expected_sales'] * 1.5, 50)
    revenue = x_units * metrics['selling_price']
    total_cost = (x_units * metrics['total_variable_cost']) + data['fixed_costs']
    profit = revenue - total_cost
    
    fig_be.add_trace(
        go.Scatter(x=x_units, y=revenue, name="Revenue", line=dict(color='green')),
        secondary_y=False,
    )
    fig_be.add_trace(
        go.Scatter(x=x_units, y=total_cost, name="Total Cost", line=dict(color='red')),
        secondary_y=False,
    )
    fig_be.add_trace(
        go.Scatter(x=x_units, y=profit, name="Profit", line=dict(color='blue'), yaxis="y2"),
        secondary_y=True,
    )
    
    fig_be.add_vline(x=metrics['break_even_units'], line_dash="dash", line_color="orange", 
                    annotation_text=f"Break-even ({metrics['break_even_units']:.0f})")
    fig_be.add_vline(x=data['expected_sales'], line_dash="dot", line_color="purple", 
                    annotation_text=f"Expected Sales")
    
    fig_be.update_layout(title="Break-even Analysis", height=400)
    st.plotly_chart(fig_be, use_container_width=True)

# Smart Insights
st.markdown("### 💡 AI-Powered Insights")

insights = []
if metrics['break_even_units'] > data['expected_sales']:
    insights.append(f"⚠️ High risk: Need {metrics['break_even_units']:.0f} units to break even vs {data['expected_sales']} expected")
elif metrics['break_even_units'] > data['expected_sales'] * 0.5:
    insights.append("📈 Moderate risk: Break-even achievable but requires strong execution")

if metrics['contribution_margin_pct'] > 0.5:
    price_increase = metrics['selling_price'] * 0.1
    profit_increase = (price_increase - metrics['total_variable_cost']) * data['expected_sales']
    insights.append(f"🚀 +10% price ($-{price_increase:.1f}) → +${profit_increase:,.0f} profit/mo")

if metrics['roi'] > 50:
    insights.append("✅ Excellent ROI - scalable business model")
elif metrics['roi'] > 20:
    insights.append("📊 Good ROI - solid foundation")

for insight in insights[:3]:  # Show top 3 insights
    st.success(insight)

# Scenario Analysis
with st.expander("🎯 Scenario Modeling", expanded=False):
    st.markdown("### Multiple Pricing Scenarios")
    
    scenarios = {
        "Conservative": {"sales": data['expected_sales'] * 0.7, "margin": data['profit_margin'] * 0.9},
        "Expected": {"sales": data['expected_sales'], "margin": data['profit_margin']},
        "Aggressive": {"sales": data['expected_sales'] * 1.3, "margin": data['profit_margin'] * 1.1}
    }
    
    scenario_data = []
    for name, params in scenarios.items():
        temp_data = data.copy()
        temp_data['expected_sales'] = params['sales']
        temp_data['profit_margin'] = params['margin']
        temp_metrics = calculate_metrics(temp_data)
        scenario_data.append({
            'Scenario': name,
            'Sales': f"{params['sales']:.0f}",
            'Price': f"${temp_metrics['selling_price']:.1f}",
            'Profit': f"${temp_metrics['monthly_profit']:,.0f}",
            'Margin': f"{temp_metrics['contribution_margin_pct']:.1f}%"
        })
    
    df_scenarios = pd.DataFrame(scenario_data)
    st.dataframe(df_scenarios, use_container_width=True)

# Export and Controls
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save Project", type="primary", use_container_width=True):
        system.save_project(st.session_state.project_name, data)
        st.success("Saved!")

with col2:
    if st.button("🔄 Reset to Defaults", type="secondary", use_container_width=True):
        st.session_state.data = {
            'material_cost': 10.0, 'packaging_cost': 2.0, 'shipping_cost': 3.0,
            'fixed_costs': 5000.0, 'profit_margin': 0.3, 'expected_sales': 1000
        }
        st.rerun()

with col3:
    # Export CSV
    export_data = {**data, **metrics}
    csv = pd.DataFrame([export_data]).to_csv(index=False)
    st.download_button(
        "📤 Export CSV", csv, f"{st.session_state.project_name}_financials.csv",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("*Built with real financial principles • Auto-saves every change • Production-ready SaaS*")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Project: {st.session_state.project_name}")
