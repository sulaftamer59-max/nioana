import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ==================== CONFIG ====================
st.set_page_config(
    page_title="🏢 BusinessPro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS FANCY UI ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
/* Main Background */
.main {background: linear-gradient(135deg, #0c0c1a 0%, #1a1a2e 50%, #16213e 100%);}
.stApp {background-color: transparent;}

/* Typography */
h1 {color: #ffffff !important; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 3.5rem !important;}
h2 {color: #e2e8f0 !important; font-family: 'Inter'; font-weight: 700; font-size: 2.2rem !important;}
h3 {color: #cbd5e1 !important; font-weight: 600;}

/* Cards */
.metric-card {
    background: linear-gradient(145deg, rgba(99, 102, 241, 0.2), rgba(234, 179, 8, 0.2)) !important;
    border-radius: 20px !important; 
    padding: 2rem !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    backdrop-filter: blur(10px) !important;
}

/* Inputs */
.stTextInput > div > div > input {
    background: linear-gradient(145deg, #f8fafc, #e2e8f0) !important;
    color: #1e293b !important;
    border-radius: 15px !important;
    border: 2px solid #cbd5e1 !important;
    padding: 15px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(45deg, #6366f1, #8b5cf6, #ec4899) !important;
    color: white !important;
    border-radius: 15px !important;
    padding: 15px 30px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 20px 40px rgba(99, 102, 241, 0.6) !important;
}

/* Sidebar */
.css-1d391kg {background: linear-gradient(180deg, rgba(12,12,26,0.95) 0%, rgba(26,26,46,0.95) 100%) !important;}
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
@st.cache_data
def init_data():
    return {
        'sales': pd.DataFrame({
            'date': pd.date_range(start='2025-11-01', periods=30, freq='D'),
            'revenue': np.random.randint(5000, 25000, 30).cumsum(),
            'orders': np.random.randint(20, 100, 30).cumsum(),
            'customers': np.random.randint(10, 50, 30).cumsum()
        }),
        'products': pd.DataFrame({
            'name': ['iPhone 16 Pro', 'MacBook Pro', 'AirPods Pro 3', 'Apple Watch Ultra', 'iPad Pro'],
            'category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
            'price': [45000, 75000, 12000, 28000, 42000],
            'stock': [50, 25, 100, 35, 40],
            'sales': np.random.randint(5, 25, 5)
        }),
        'kpis': {
            'total_revenue': 2450000,
            'total_orders': 1560,
            'total_customers': 890,
            'growth_rate': 24.5
        }
    }

if 'data' not in st.session_state:
    st.session_state.data = init_data()

# ==================== HEADER ====================
def render_header():
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(45deg, #6366f1, #8b5cf6); 
                    padding: 1.5rem; border-radius: 20px; text-align: center;'>
            <h1 style='color: white; margin: 0;'>🏢</h1>
            <p style='color: white; margin: 0.5rem 0 0 0; font-weight: 600;'>BusinessPro</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>📊 Business Analytics Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.3rem;'>Real-time insights for smart decisions</p>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(45deg, #10b981, #059669); 
                    padding: 1.5rem; border-radius: 20px; text-align: center;'>
            <h3 style='color: white; margin: 0;'>EGP</h3>
            <p style='color: white; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;'>2.45M</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== METRICS ====================
def render_metrics():
    data = st.session_state.data
    kpis = data['kpis']
    
    col1, col2, col3, col4 = st.columns(4, gap="2rem")
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>💰 Total Revenue</h3>
            <h1 style='color: #10b981; font-size: 2.5rem;'>EGP 2.45M</h1>
            <p style='color: #94a3b8;'>+24.5% from last month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>📦 Total Orders</h3>
            <h1 style='color: #3b82f6; font-size: 2.5rem;'>1,560</h1>
            <p style='color: #94a3b8;'>+18.2% growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>👥 Active Customers</h3>
            <h1 style='color: #f59e0b; font-size: 2.5rem;'>890</h1>
            <p style='color: #94a3b8;'>+12.7% new users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='metric-card'>
            <h3>📈 Conversion Rate</h3>
            <h1 style='color: #ef4444; font-size: 2.5rem;'>4.2%</h1>
            <p style='color: #94a3b8;'>Target: 5%</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== CHARTS ====================
def render_charts():
    data = st.session_state.data
    sales_data = data['sales']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue Chart
        fig_revenue = px.line(sales_data, x='date', y='revenue', 
                             title="💵 Revenue Trend",
                             color_discrete_sequence=['#6366f1'])
        fig_revenue.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': '#e2e8f0'}
        })
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Orders Chart
        fig_orders = px.bar(sales_data.tail(14), x='date', y='orders',
                           title="📦 Orders (Last 2 Weeks)",
                           color_discrete_sequence=['#3b82f6'])
        fig_orders.update_layout({
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': '#e2e8f0'}
        })
        st.plotly_chart(fig_orders, use_container_width=True)

# ==================== PRODUCTS TABLE ====================
def render_products():
    data = st.session_state.data
    products = data['products']
    
    st.markdown("### 📱 Top Products Performance")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.dataframe(products.style.format({
            'price': 'EGP {:,.0f}',
            'sales': '{:,.0f}'
        }), use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(145deg, #10b981, #059669); 
                    color: white; padding: 2rem; border-radius: 20px; text-align: center; height: 300px;'>
            <h3 style='margin-top: 0;'>🎯 Quick Actions</h3>
            <p>📈 View Reports</p>
            <p>➕ Add Product</p>
            <p>👥 Manage Customers</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== SIDEBAR CONTROLS ====================
def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Controls")
        
        # Date Range
        date_range = st.date_input("Select Date Range", 
                                 value=(datetime.now()-timedelta(days=30), datetime.now()))
        
        # Filters
        category = st.selectbox("Product Category", 
                              options=['All', 'Electronics', 'Clothing', 'Accessories'])
        
        # Refresh Button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.data = init_data()
            st.success("✅ Data refreshed!")
            st.rerun()

# ==================== MAIN APP ====================
def main():
    render_header()
    st.markdown("---")
    
    render_sidebar()
    
    render_metrics()
    st.markdown("---")
    
    render_charts()
    st.markdown("---")
    
    render_products()

if __name__ == "__main__":
    main()
