import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Business Dashboard")
st.title("📊 Product Analytics Dashboard")

# جدول فارغ لإدخال المنتجات
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['Product', 'Price', 'Cost', 'Sold', 'Stock'])

st.subheader("🛒 Add Your Products (Click + to add)")

# الجدول الرئيسي
edited_df = st.data_editor(
    st.session_state.df,
    column_config={
        "Product": st.column_config.TextColumn("Product Name"),
        "Price": st.column_config.NumberColumn("Price ($)", format="%.0f"),
        "Cost": st.column_config.NumberColumn("Cost ($)", format="%.0f"),
        "Sold": st.column_config.NumberColumn("Units Sold"),
        "Stock": st.column_config.NumberColumn("Stock")
    },
    num_rows="dynamic",
    use_container_width=True
)

st.session_state.df = edited_df
df = st.session_state.df.copy()

# التحقق من البيانات والحسابات البسيطة
valid_data = df.dropna(subset=['Sold']).copy()
if len(valid_data) > 0 and valid_data['Sold'].sum() > 0:
    # تحويل لأرقام
    valid_data['Price'] = pd.to_numeric(valid_data['Price'], errors='coerce').fillna(0)
    valid_data['Cost'] = pd.to_numeric(valid_data['Cost'], errors='coerce').fillna(0)
    valid_data['Sold'] = pd.to_numeric(valid_data['Sold'], errors='coerce').fillna(0)
    
    # الحسابات
    valid_data['Revenue'] = valid_data['Price'] * valid_data['Sold']
    valid_data['Profit'] = valid_data['Revenue'] - (valid_data['Cost'] * valid_data['Sold'])
    valid_data['Margin'] = (valid_data['Profit'] / valid_data['Revenue'].replace(0, 1) * 100).round(1)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue", f"${valid_data['Revenue'].sum():,.0f}")
    col2.metric("💵 Total Profit", f"${valid_data['Profit'].sum():,.0f}")
    col3.metric("📦 Units Sold", f"{valid_data['Sold'].sum():,.0f}")
    col4.metric("📊 Avg Margin", f"{valid_data['Margin'].mean():.1f}%")
    
    # أفضل المنتجات
    st.subheader("🏆 Top Products")
    top_products = valid_data.nlargest(3, 'Revenue')[['Product', 'Revenue', 'Profit', 'Margin']]
    st.dataframe(top_products.round(1))
    
    # رسوم بيانية بسيطة بدون plotly
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue vs Profit")
        st.scatter_chart(valid_data, x='Revenue', y='Profit', size='Sold')
    
    with col2:
        st.subheader("Profit Margin")
        margin_chart = valid_data.sort_values('Margin')[['Product', 'Margin']].set_index('Product')
        st.bar_chart(margin_chart['Margin'])
    
    # التقرير الكامل
    st.subheader("📋 Full Report")
    display_df = valid_data[['Product', 'Price', 'Cost', 'Sold', 'Stock', 'Revenue', 'Profit', 'Margin']].round(1)
    st.dataframe(display_df)

else:
    # عرض فارغ
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue", "$0")
    col2.metric("💵 Total Profit", "$0")
    col3.metric("📦 Units Sold", "0")
    col4.metric("📊 Avg Margin", "0%")
    
    st.info("👆 Click **+** above to add products!")
    
    st.markdown("""
    ### Quick Start Guide:
    1. Click **+** button 
    2. Enter **Product Name**
    3. Enter **Price per unit**
    4. Enter **Cost per unit**
    5. Enter **Units Sold**
    6. Enter **Current Stock**
    """)

# Sidebar
with st.sidebar:
    st.header("🎯 Instructions")
    
    if st.button("🧪 Load Sample Data"):
        st.session_state.df = pd.DataFrame({
            'Product': ['iPhone 15', 'MacBook Air', 'AirPods Pro'],
            'Price': [1200, 1299, 249],
            'Cost': [850, 950, 160],
            'Sold': [25, 12, 45],
            'Stock': [75, 38, 155]
        })
        st.rerun()
    
    st.markdown("""
    **Works instantly:**
    - Add rows with **+ button**
    - Edit any cell
    - Charts update **automatically**
    """)
