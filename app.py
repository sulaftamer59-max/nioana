import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Business Dashboard")
st.title("📊 Product Analytics Dashboard")

# جدول فارغ تماماً لإدخال المنتجات
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['Product', 'Price', 'Cost', 'Sold', 'Stock'])

st.subheader("🛒 **Add Your Products Here** (Click + to add)")

# الجدول الرئيسي
edited_df = st.data_editor(
    st.session_state.df,
    column_config={
        "Product": st.column_config.TextColumn("Product Name", required=True),
        "Price": st.column_config.NumberColumn("Price ($)", format="%.0f", required=True),
        "Cost": st.column_config.NumberColumn("Cost ($)", format="%.0f", required=True),
        "Sold": st.column_config.NumberColumn("Units Sold", min_value=0),
        "Stock": st.column_config.NumberColumn("Stock", min_value=0)
    },
    num_rows="dynamic",
    use_container_width=True,
    key="product_table"
)

st.session_state.df = edited_df
df = st.session_state.df.copy()

# التحليلات
if len(df) > 0 and df['Sold'].sum() > 0:
    df['Revenue'] = pd.to_numeric(df['Price'], errors='coerce') * pd.to_numeric(df['Sold'], errors='coerce')
    df['Profit'] = df['Revenue'] - (pd.to_numeric(df['Cost'], errors='coerce') * pd.to_numeric(df['Sold'], errors='coerce'))
    df['Margin'] = (df['Profit'] / df['Revenue'].replace(0, 1) * 100).round(1)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue", f"${df['Revenue'].sum():,.0f}")
    col2.metric("💵 Total Profit", f"${df['Profit'].sum():,.0f}")
    col3.metric("📦 Units Sold", f"{df['Sold'].sum():,.0f}")
    col4.metric("📊 Avg Margin", f"{df['Margin'].mean():.1f}%")
    
    # أفضل المنتجات
    st.subheader("🏆 Top Products")
    top = df.nlargest(3, 'Revenue')[['Product', 'Revenue', 'Profit', 'Margin']]
    st.dataframe(top)
    
    # الرسوم البيانية بالأسهم العادية (غير wireframe)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue vs Profit")
        fig1 = px.scatter(df, x='Revenue', y='Profit', 
                         size='Sold', hover_name='Product',
                         title="Revenue vs Profit (Arrows)",
                         size_max=40)
        fig1.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("📊 Profit Margin Ranking")
        fig2 = px.bar(df.sort_values('Margin', ascending=True), 
                     x='Margin', y='Product',
                     orientation='h',
                     title="Profit Margin %",
                     color='Margin',
                     color_continuous_scale='RdYlGn')
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    # التقرير الكامل
    st.subheader("📋 Complete Report")
    display_df = df[['Product', 'Price', 'Cost', 'Sold', 'Stock', 'Revenue', 'Profit', 'Margin']]
    st.dataframe(display_df.round(1))

else:
    st.info("👆 **Click the + button above to add your products!**")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue", "$0")
    col2.metric("💵 Total Profit", "$0")
    col3.metric("📦 Units Sold", "0")
    col4.metric("📊 Avg Margin", "0%")
    
    st.markdown("### 📝 **Quick Start:**")
    st.markdown("""
    1. Click **+** to add a row
    2. Enter **Product name**
    3. Enter **Price** and **Cost**
    4. Enter **Sold** units
    5. Enter **Stock** level
    6. Charts update **automatically**!
    """)

# Sidebar
with st.sidebar:
    st.header("🎯 How To Use")
    
    st.markdown("""
    **Step by Step:**
    1. **Click +** in table above
    2. Fill **Product details**
    3. Analytics **update instantly**
    
    **Example Data:**
    ```
    Product: iPhone 15
    Price: 1200
    Cost: 850  
    Sold: 25
    Stock: 75
    ```
    """)
    
    if st.button("🧪 Load Sample Data"):
        st.session_state.df = pd.DataFrame({
            'Product': ['iPhone 15 Pro', 'MacBook Air', 'AirPods Pro'],
            'Price': [1200, 1299, 249],
            'Cost': [850, 950, 160],
            'Sold': [25, 12, 45],
            'Stock': [75, 38, 155]
        })
        st.rerun()
