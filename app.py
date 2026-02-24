import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ==================== CONFIG ====================
st.set_page_config(
    page_title="🏢 BusinessPro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.main {background: linear-gradient(135deg, #0c0c1a 0%, #1a1a2e 50%, #16213e 100%);}
h1 {color: #ffffff !important; font-size: 3rem !important; font-weight: 700;}
h2, h3 {color: #e2e8f0 !important;}
.stTextInput input {background: #f8fafc; color: #1e293b; border-radius: 10px;}
.stButton > button {background: linear-gradient(45deg, #6366f1, #8b5cf6); color: white; border-radius: 10px; font-weight: 600;}
.metric-card {background: rgba(99,102,241,0.2); padding: 1.5rem; border-radius: 15px; border: 1px solid rgba(99,102,241,0.3);}
</style>
""", unsafe_allow_html=True)

# ==================== DATA ====================
@st.cache_data(ttl=300)
def load_data():
    dates = pd.date_range(start='2025-12-01', periods=30, freq='D')
    return {
        'sales': pd.DataFrame({
            'date': dates,
            'revenue': np.random.randint(8000, 30000, 30).cumsum(),
            'orders': np.random.randint(25, 120, 30).cumsum(),
            'customers': np.random.randint(15, 60, 30)
        }),
        'products': pd.DataFrame({
            'name': ['iPhone 16 Pro', 'MacBook Pro M4', 'AirPods Pro 3', 'Apple Watch Ultra 2', 'iPad Pro M4'],
            'price': [45000, 78000, 12900, 32000, 48000],
            'stock': [45, 22, 95, 38, 35],
            'sales': np.random.randint(8, 35, 5)
        })
    }

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# ==================== HEADER ====================
st.markdown("# 📊 **BusinessPro Dashboard**")
st.markdown("### *Real-time analytics for smart decisions*")

# ==================== METRICS ====================
data = st.session_state.data
sales = data['sales']
products = data['products']

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='metric-card'>
        <h3>Total Revenue</h3>
        <h1>EGP {:.0f}</h1>
        <p>+{:.1f}% MoM</p>
    </div>
    """.format(sales['revenue'].iloc[-1]/1000, 25.3), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='metric-card'>
        <h3>Total Orders</h3>
        <h1>{:,}</h1>
        <p>+18.2% growth</p>
    </div>
    """.format(sales['orders'].iloc[-1]), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='metric-card'>
        <h3>Customers</h3>
        <h1>{:,}</h1>
        <p>+14.7% new</p>
    </div>
    """.format(sales['customers'].sum()), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='metric-card'>
        <h3>Conversion</h3>
        <h1>4.8%</h1>
        <p>Target: 6%</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== CHARTS ====================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 **Revenue Trend**")
    fig1 = px.line(sales.tail(14), x='date', y='revenue', 
                   color_discrete_sequence=['#6366f1'],
                   title="Last 2 Weeks")
    fig1.update_layout(showlegend=False, font=dict(color="#e2e8f0"))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### 📦 **Daily Orders**")
    fig2 = px.bar(sales.tail(7), x='date', y='orders',
                  color_discrete_sequence=['#3b82f6'])
    fig2.update_layout(showlegend=False, font=dict(color="#e2e8f0"))
    st.plotly_chart(fig2, use_container_width=True)

# ==================== PRODUCTS ====================
st.markdown("### 📱 **Top Products**")
col1, col2 = st.columns([3,1])

with col1:
    products_display = products.copy()
    products_display['revenue'] = products_display['price'] * products_display['sales']
    products_display = products_display.sort_values('revenue', ascending=False)
    st.dataframe(products_display.round(0), use_container_width=True)

with col2:
    st.markdown("""
    <div style='background: linear-gradient(145deg, #10b981, #059669); 
                color: white; padding: 2rem; border-radius: 15px; text-align: center;'>
        <h3>🚀 Quick Actions</h3>
        <p>➕ Add Product</p>
        <p>📊 Full Report</p>
        <p>👥 Customers</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## ⚙️ **Controls**")
    
    if st.button("🔄 **Refresh Data**"):
        st.session_state.data = load_data()
        st.success("✅ Data refreshed!")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📅 **Date Filter**")
    date_range = st.date_input("Select period", 
                              value=(datetime.now()-timedelta(days=30), datetime.now()))
    
    st.markdown("### 🏷️ **Category**")
    category = st.selectbox("Filter by", ["All Products", "Electronics", "Clothing"])
