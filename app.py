import streamlit as st
import pandas as pd

# الإعدادات الأساسية
st.set_page_config(layout="wide", page_title="Business Dashboard")
st.title("📊 Product Analytics Dashboard")

# البيانات الوهمية جاهزة تلقائياً
sample_data = {
    'Product': ['iPhone 15 Pro', 'MacBook Air M3', 'AirPods Pro 3', 'Samsung S24 Ultra', 'iPad Pro'],
    'Price': [1200, 1299, 249, 1350, 1299],
    'Cost': [850, 950, 160, 950, 900],
    'Sold': [25, 12, 45, 18, 8],
    'Stock': [75, 38, 155, 62, 42]
}

# إنشاء الجدول
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(sample_data)

# الجدول القابل للتعديل
edited_df = st.data_editor(
    st.session_state.df,
    column_config={
        "Product": st.column_config.TextColumn("Product Name"),
        "Price": st.column_config.NumberColumn("Price ($)", format="%.0f"),
        "Cost": st.column_config.NumberColumn("Cost ($)", format="%.0f"),
        "Sold": st.column_config.NumberColumn("Units Sold"),
        "Stock": st.column_config.NumberColumn("Current Stock")
    },
    num_rows="dynamic",
    use_container_width=True,
    key="main_table"
)

st.session_state.df = edited_df
df = st.session_state.df.copy()

# الحسابات التلقائية
df['Revenue'] = pd.to_numeric(df['Price'], errors='coerce') * pd.to_numeric(df['Sold'], errors='coerce')
df['Profit'] = df['Revenue'] - (pd.to_numeric(df['Cost'], errors='coerce') * pd.to_numeric(df['Sold'], errors='coerce'))
df['Margin'] = (df['Profit'] / df['Revenue'].replace(0, 1) * 100).round(1)

# عرض البيانات الحالية
st.subheader("📈 Analytics")
col1, col2, col3, col4 = st.columns(4)

total_revenue = df['Revenue'].sum()
total_profit = df['Profit'].sum()
total_sold = df['Sold'].sum()
avg_margin = df['Margin'].mean()

col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Total Profit", f"${total_profit:,.0f}")
col3.metric("Units Sold", f"{total_sold:,.0f}")
col4.metric("Avg Profit Margin", f"{avg_margin:.1f}%")

# أفضل المنتجات
st.subheader("🏆 Top Products by Revenue")
top_products = df.nlargest(3, 'Revenue')[['Product', 'Revenue', 'Profit', 'Margin']]
st.dataframe(top_products.style.format({
    'Revenue': '${:,.0f}',
    'Profit': '${:,.0f}',
    'Margin': '{:.1f}%'
}))

# الرسوم البيانية
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Revenue vs Profit")
    st.scatter_chart(df, x='Revenue', y='Profit', size='Sold')

with col2:
    st.subheader("📈 Profit Margin")
    margin_data = df.sort_values('Margin')[['Product', 'Margin']].set_index('Product')
    st.bar_chart(margin_data['Margin'])

# التقرير الكامل
st.subheader("📋 Full Report")
display_df = df[['Product', 'Price', 'Cost', 'Sold', 'Stock', 'Revenue', 'Profit', 'Margin']].round(1)
st.dataframe(display_df.style.format({
    'Price': '${:,.0f}',
    'Cost': '${:,.0f}',
    'Revenue': '${:,.0f}',
    'Profit': '${:,.0f}',
    'Margin': '{:.1f}%'
}))

# الشريط الجانبي
with st.sidebar:
    st.header("🎯 Instructions")
    st.markdown("""
    **Already loaded with sample data!**
    
    1. ✅ Table is ready with 5 products
    2. ✏️ Click any cell to edit
    3. ➕ Click **+** to add more products
    4. 🗑️ Click **trash** to delete rows
    5. 📊 Analytics update **instantly**
    
    **Columns:**
    - Product: Product name
    - Price: Selling price per unit
    - Cost: Cost per unit
    - Sold: Total units sold
    - Stock: Current inventory
    """)
    
    if st.button("🔄 Reset Sample Data"):
        st.session_state.df = pd.DataFrame(sample_data)
        st.rerun()
