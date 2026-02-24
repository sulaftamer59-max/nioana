import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import numpy as np

# ==================== CONFIG ====================
st.set_page_config(
    page_title="🏢 BusinessPro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS الفخم ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.main {background: linear-gradient(135deg, #0c0c1a 0%, #1a1a2e 50%, #16213e 100%);}
h1 {color: #ffffff !important; font-size: 3rem !important; font-weight: 700;}
h2, h3 {color: #e2e8f0 !important;}
.metric-card {background: rgba(99,102,241,0.2); padding: 1.5rem; border-radius: 15px; border: 1px solid rgba(99,102,241,0.3);}
.metric-card-green {background: rgba(34,197,94,0.2); border: 1px solid rgba(34,197,94,0.3);}
.metric-card-red {background: rgba(239,68,68,0.2); border: 1px solid rgba(239,68,68,0.3);}
.stDataEditor {background: rgba(30,30,63,0.9);}
</style>
""", unsafe_allow_html=True)

# ==================== بيانات افتراضية ====================
@st.cache_data
def create_sample_data():
    return pd.DataFrame({
        'product_name': ['iPhone 16 Pro', 'MacBook Pro', 'AirPods Pro 3', 'Samsung S25 Ultra', 'iPad Pro', 'Apple Watch', 'Sony WH-1000XM6'],
        'price': [45000, 78000, 12900, 42000, 48000, 32000, 15000],
        'cost': [32000, 55000, 8500, 29000, 34000, 21000, 9500],
        'quantity_sold': [25, 12, 45, 18, 10, 32, 28],
        'stock': [100, 50, 200, 75, 40, 120, 90]
    })

if 'products_df' not in st.session_state:
    st.session_state.products_df = create_sample_data()

# ==================== HEADER ====================
st.markdown("# 📊 **لوحة تحكم المبيعات المتكاملة**")
st.markdown("### *ادخل بيانات منتجاتك وشاهد التحليلات المتقدمة*")

# ==================== جدول إدخال المنتجات ====================
st.markdown("### 🛒 **بيانات المنتجات**")
st.markdown("*املأ الجدول أو عدّل القيم حسب بياناتك*")

def update_dataframe(df):
    st.session_state.products_df = df
    st.rerun()

edited_df = st.data_editor(
    st.session_state.products_df,
    column_config={
        "product_name": st.column_config.TextColumn("اسم المنتج", help="اسم المنتج بالكامل"),
        "price": st.column_config.NumberColumn("سعر البيع", format="%.0f ج.م", min_value=0),
        "cost": st.column_config.NumberColumn("تكلفة الشراء", format="%.0f ج.م", min_value=0),
        "quantity_sold": st.column_config.NumberColumn("الكمية المباعة", min_value=0),
        "stock": st.column_config.NumberColumn("المخزون الحالي", min_value=0)
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=False
)

if edited_df.equals(st.session_state.products_df):
    pass
else:
    update_dataframe(edited_df)

df = st.session_state.products_df

# ==================== حساب المؤشرات المالية ====================
df['revenue'] = df['price'] * df['quantity_sold']
df['profit'] = df['revenue'] - (df['cost'] * df['quantity_sold'])
df['profit_margin'] = (df['profit'] / df['revenue'] * 100).round(1)
df['roi'] = ((df['profit'] / (df['cost'] * df['quantity_sold'])) * 100).round(1)

# ==================== KPIs الرئيسية ====================
col1, col2, col3, col4 = st.columns(4)

total_revenue = df['revenue'].sum()
total_profit = df['profit'].sum()
total_cost = (df['cost'] * df['quantity_sold']).sum()
avg_profit_margin = df['profit_margin'].mean()

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>💰 الإيرادات الإجمالية</h3>
        <h1>{total_revenue:,.0f} ج.م</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card-green'>
        <h3>💵 الربح الصافي</h3>
        <h1>{total_profit:,.0f} ج.م</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>📦 الكمية المباعة</h3>
        <h1>{df['quantity_sold'].sum():,.0f}</h1>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>📊 هامش الربح المتوسط</h3>
        <h1>{avg_profit_margin:.1f}%</h1>
    </div>
    """, unsafe_allow_html=True)

# ==================== المنتجات الأفضل والأسوأ ====================
st.markdown("### 🔥 **أداء المنتجات**")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏆 **أفضل المنتجات (Best Sellers)**")
    top_products = df.nlargest(3, 'revenue')[['product_name', 'revenue', 'profit_margin']]
    st.dataframe(top_products.style.format({
        'revenue': '{:,.0f} ج.م',
        'profit_margin': '{:.1f}%'
    }), use_container_width=True)

with col2:
    st.markdown("#### 📉 **المنتجات الضعيفة**")
    weak_products = df.nsmallest(3, 'revenue')[['product_name', 'revenue', 'profit_margin']]
    st.dataframe(weak_products.style.format({
        'revenue': '{:,.0f} ج.م',
        'profit_margin': '{:.1f}%'
    }), use_container_width=True)

# ==================== الرسوم البيانية ====================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💹 **الإيرادات مقابل الربح**")
    fig1 = px.scatter(df, x='revenue', y='profit', size='quantity_sold',
                     hover_name='product_name', size_max=60,
                     title="حجم المبيعات مقابل الربح")
    fig1.update_layout(font=dict(color="#e2e8f0"))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### 📊 **هامش الربح لكل منتج**")
    fig2 = px.bar(df.sort_values('profit_margin', ascending=True), 
                 x='profit_margin', y='product_name',
                 orientation='h', title="هامش الربح (%)")
    fig2.update_layout(font=dict(color="#e2e8f0"))
    st.plotly_chart(fig2, use_container_width=True)

# ==================== جدول شامل ====================
st.markdown("### 📈 **تقرير شامل للمنتجات**")
st.dataframe(df[['product_name', 'price', 'cost', 'quantity_sold', 'revenue', 'profit', 'profit_margin', 'roi', 'stock']].round(1).style.format({
    'price': '{:,.0f} ج.م',
    'cost': '{:,.0f} ج.م',
    'revenue': '{:,.0f} ج.م',
    'profit': '{:,.0f} ج.م',
    'profit_margin': '{:.1f}%',
    'roi': '{:.1f}%'
}), use_container_width=True)

# ==================== تحليلات إضافية ====================
st.markdown("### 🎯 **تحليلات ذكية**")

col1, col2, col3, col4 = st.columns(4)
high_roi = df['roi'].max()
low_stock = df[df['stock'] < 20].shape[0]
most_profitable = df.loc[df['profit'].idxmax(), 'product_name']
total_roi = df['roi'].mean()

with col1:
    st.metric("أعلى عائد استثمار", f"{high_roi:.1f}%")
with col2:
    st.metric("منتجات قليلة المخزون", f"{low_stock}")
with col3:
    st.metric("الأكثر ربحية", most_profitable[:15])
with col4:
    st.metric("متوسط العائد", f"{total_roi:.1f}%")

# ==================== نصائح تلقائية ====================
st.markdown("### 💡 **توصيات تلقائية**")

recommendations = []
if low_stock > 0:
    recommendations.append("⚠️  إعادة تعبئة المخزون للمنتجات القليلة")
if df['profit_margin'].mean() < 25:
    recommendations.append("📈  راجع أسعار البيع (هامش ربح منخفض)")
if (df['stock'] > 50).sum() > 2:
    recommendations.append("🗑️  قلل المخزون الزائد لبعض المنتجات")

for rec in recommendations:
    st.warning(rec)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🎛️ **إعدادات سريعة**")
    
    if st.button("🆕 **بيانات تجريبية**", use_container_width=True):
        st.session_state.products_df = create_sample_data()
        st.success("✅ تم تحميل بيانات تجريبية")
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 📋 **كيف تستخدم:**
    1. عدّل أسماء المنتجات
    2. أدخل **سعر البيع** و**تكلفة الشراء**
    3. أدخل **الكمية المباعة**
    4. أدخل **المخزون الحالي**
    5. **التحليلات تتحدث تلقائياً!**
    """)
