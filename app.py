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
.empty-placeholder {background: rgba(50,50,80,0.5); color: #94a3b8; padding: 3rem; border-radius: 15px; border: 2px dashed #6366f1; text-align: center;}
</style>
""", unsafe_allow_html=True)

# ==================== جدول فارغ تماماً ====================
st.markdown("# 📊 **لوحة تحكم المبيعات المتكاملة**")
st.markdown("### *املأ الجدول أدناه لرؤية التحليلات المتقدمة*")

# جدول فارغ لإدخال البيانات
st.markdown("### 🛒 **بيانات المنتجات** *(اضغط على + لإضافة منتج)*")

empty_df = pd.DataFrame({
    'product_name': [''],
    'price': [0],
    'cost': [0],
    'quantity_sold': [0],
    'stock': [0]
})

if 'products_df' not in st.session_state:
    st.session_state.products_df = empty_df

def update_dataframe(df):
    st.session_state.products_df = df
    st.rerun()

edited_df = st.data_editor(
    st.session_state.products_df,
    column_config={
        "product_name": st.column_config.TextColumn(
            "اسم المنتج", 
            help="اكتب اسم المنتج هنا",
            required=True
        ),
        "price": st.column_config.NumberColumn(
            "سعر البيع (ج.م)", 
            format="%.0f ج.م", 
            min_value=0,
            required=True
        ),
        "cost": st.column_config.NumberColumn(
            "تكلفة الشراء (ج.م)", 
            format="%.0f ج.م", 
            min_value=0,
            required=True
        ),
        "quantity_sold": st.column_config.NumberColumn(
            "الكمية المباعة", 
            min_value=0,
            help="كم وحدة بيعت من المنتج"
        ),
        "stock": st.column_config.NumberColumn(
            "المخزون الحالي", 
            min_value=0,
            help="المتبقي في المخزن"
        )
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=False
)

# تحديث البيانات
if not edited_df.equals(st.session_state.products_df):
    st.session_state.products_df = edited_df

df = st.session_state.products_df

# ==================== التحقق من وجود بيانات ====================
has_data = (df['price'] > 0).sum() > 0 or (df['quantity_sold'] > 0).sum() > 0

# ==================== KPIs ====================
col1, col2, col3, col4 = st.columns(4)

if has_data:
    # حساب المؤشرات المالية
    df['revenue'] = df['price'] * df['quantity_sold']
    df['profit'] = df['revenue'] - (df['cost'] * df['quantity_sold'])
    df['profit_margin'] = (df['profit'] / df['revenue'].replace(0, 1) * 100).round(1)
    df['roi'] = ((df['profit'] / (df['cost'] * df['quantity_sold'].replace(0, 1))) * 100).round(1)
    
    total_revenue = df['revenue'].sum()
    total_profit = df['profit'].sum()
    total_sold = df['quantity_sold'].sum()
    avg_margin = df['profit_margin'].mean()
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>💰 الإيرادات</h3>
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
            <h3>📦 مبيعات</h3>
            <h1>{total_sold:,.0f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>📊 هامش الربح</h3>
            <h1>{avg_margin:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== أفضل/أسوأ المنتجات ====================
    st.markdown("### 🔥 **أداء المنتجات**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 **أفضل المبيعات**")
        top_products = df.nlargest(5, 'revenue')[['product_name', 'revenue', 'profit_margin']]
        if not top_products.empty:
            st.dataframe(top_products.style.format({
                'revenue': '{:,.0f} ج.م',
                'profit_margin': '{:.1f}%'
            }).background_gradient(subset=['revenue'], cmap='Greens'), use_container_width=True)
    
    with col2:
        st.markdown("#### 📉 **أقل المبيعات**")
        bottom_products = df.nsmallest(5, 'revenue')[['product_name', 'revenue', 'profit_margin']]
        if not bottom_products.empty:
            st.dataframe(bottom_products.style.format({
                'revenue': '{:,.0f} ج.م',
                'profit_margin': '{:.1f}%'
            }).background_gradient(subset=['revenue'], cmap='Reds'), use_container_width=True)
    
    # ==================== الرسوم البيانية ====================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💹 **الإيرادات مقابل الربح**")
        fig1 = px.scatter(df[df['revenue'] > 0], x='revenue', y='profit', 
                         size='quantity_sold', hover_name='product_name',
                         title="حجم المبيعات × الربح", size_max=50)
        fig1.update_layout(font=dict(color="#e2e8f0"), showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 **هامش الربح**")
        fig2 = px.bar(df[df['revenue'] > 0].sort_values('profit_margin'), 
                     x='profit_margin', y='product_name', orientation='h',
                     title="نسبة الربح لكل منتج (%)")
        fig2.update_layout(font=dict(color="#e2e8f0"))
        st.plotly_chart(fig2, use_container_width=True)
    
    # ==================== التقرير الشامل ====================
    st.markdown("### 📈 **التقرير الشامل**")
    display_df = df[['product_name', 'price', 'cost', 'quantity_sold', 'revenue', 'profit', 'profit_margin', 'stock']].round(1)
    st.dataframe(display_df.style.format({
        'price': '{:,.0f} ج.م',
        'cost': '{:,.0f} ج.م',
        'revenue': '{:,.0f} ج.م',
        'profit': '{:,.0f} ج.م',
        'profit_margin': '{:.1f}%'
    }).background_gradient(subset=['profit_margin'], cmap='RdYlGn'), use_container_width=True)

else:
    # ==================== مكان فارغ للـ KPIs ====================
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='empty-placeholder'>
            <h3>💰 الإيرادات</h3>
            <h1>0 ج.م</h1>
            <p>ابدأ بإدخال البيانات</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='empty-placeholder'>
            <h3>💵 الربح</h3>
            <h1>0 ج.م</h1>
            <p>املأ الجدول أعلاه</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='empty-placeholder'>
            <h3>📦 المبيعات</h3>
            <h1>0</h1>
            <p>لا توجد بيانات</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class='empty-placeholder'>
            <h3>📊 هامش الربح</h3>
            <h1>0%</h1>
            <p>انتظر التحليل</p>
        </div>
        """, unsafe_allow_html=True)
    
    # مكان فارغ للرسوم
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='empty-placeholder' style='height: 400px; display: flex; align-items: center; justify-content: center;'>
            <h3>💹 الرسم البياني</h3>
            <p>ابدأ بإدخال المنتجات</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='empty-placeholder' style='height: 400px; display: flex; align-items: center; justify-content: center;'>
            <h3>📊 هامش الربح</h3>
            <p>ستظهر هنا بعد إدخال البيانات</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='empty-placeholder'>
        <h3>📈 التقرير الشامل</h3>
        <p>✅ اضغط على <strong>+</strong> في الجدول أعلاه<br>
        ✅ أدخل اسم المنتج وسعره وتكلفته<br>
        ✅ أدخل الكمية المباعة والمخزون<br>
        ✅ التحليلات ستظهر تلقائياً!</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🎛️ **دليل سريع**")
    st.markdown("""
    ### 📝 **خطوات الاستخدام:**
    1. **اضغط +** في الجدول لإضافة منتج
    2. اكتب **اسم المنتج**
    3. أدخل **سعر البيع** و**تكلفة الشراء**
    4. اكتب **الكمية المباعة**
    5. أدخل **المخزون الحالي**
    
    **التحليلات تتحدث تلقائياً فور الإدخال!** ✨
    """)
    
    if st.button("📊 **عرض بيانات تجريبية**", use_container_width=True):
        st.session_state.products_df = pd.DataFrame({
            'product_name': ['iPhone 16 Pro', 'MacBook Pro', 'AirPods Pro 3'],
            'price': [45000, 78000, 12900],
            'cost': [32000, 55000, 8500],
            'quantity_sold': [25, 12, 45],
            'stock': [75, 38, 155]
        })
        st.rerun()
