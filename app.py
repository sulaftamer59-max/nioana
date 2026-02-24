import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Business Dashboard")

st.title("📊 Business Dashboard")

# Empty table for data entry
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'Product': [""],
        'Price': [0],
        'Cost': [0],
        'Sold': [0],
        'Stock': [0]
    })

df = st.data_editor(
    st.session_state.data,
    column_config={
        "Product": st.column_config.TextColumn("Product Name"),
        "Price": st.column_config.NumberColumn("Price ($)", format="%.2f"),
        "Cost": st.column_config.NumberColumn("Cost ($)", format="%.2f"),
        "Sold": st.column_config.NumberColumn("Units Sold"),
        "Stock": st.column_config.NumberColumn("Stock Level")
    },
    num_rows="dynamic",
    use_container_width=True
)

st.session_state.data = df

# Analytics when data exists
if len(df) > 0 and df['Sold'].sum() > 0:
    df['Revenue'] = df['Price'] * df['Sold']
    df['Profit'] = df['Revenue'] - (df['Cost'] * df['Sold'])
    df['Margin'] = (df['Profit'] / df['Revenue'] * 100).round(1)
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"${df['Revenue'].sum():,.2f}")
    with col2:
        st.metric("Total Profit", f"${df['Profit'].sum():,.2f}")
    with col3:
        st.metric("Avg Margin", f"{df['Margin'].mean():.1f}%")
    
    # Top products
    st.subheader("🏆 Top Products")
    top = df.nlargest(3, 'Revenue')[['Product', 'Revenue', 'Profit']]
    st.dataframe(top)
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue vs Profit")
        st.scatter_chart(df, x='Revenue', y='Profit', size='Sold')
    
    with col2:
        st.subheader("Profit Margin")
        margin_df = df.sort_values('Margin')
        st.bar_chart(margin_df.set_index('Product')['Margin'])
    
    # Full report
    st.subheader("📋 Full Report")
    st.dataframe(df[['Product', 'Price', 'Cost', 'Sold', 'Revenue', 'Profit', 'Margin', 'Stock']])

else:
    st.info("👆 **Click + above to add products and see analytics instantly**")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue", "$0")
    col2.metric("Profit", "$0") 
    col3.metric("Margin", "0%")

# Sidebar
with st.sidebar:
    st.header("📝 How to use:")
    st.markdown("""
    1. **Click +** to add row
    2. **Fill product details**
    3. **Analytics update automatically**
    
    **Columns:**
    - Product: Product name
    - Price: Selling price
    - Cost: Purchase cost  
    - Sold: Units sold
    - Stock: Current inventory
    """)
    
    if st.button("🧪 Sample Data"):
        st.session_state.data = pd.DataFrame({
            'Product': ['iPhone 15', 'MacBook Air', 'AirPods'],
            'Price': [999, 1299, 199],
            'Cost': [700, 900, 130],
            'Sold': [25, 12, 45],
            'Stock': [75, 38, 155]
        })
        st.rerun()
