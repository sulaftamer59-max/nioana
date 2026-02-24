import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import numpy as np

# ==================== CONFIG ====================
st.set_page_config(
    page_title="🏢 BusinessPro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS الناعم والسلس ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.main {background: linear-gradient(135deg, #0c0c1a 0%, #1a1a2e 50%, #16213e 100%);}
h1 {color: #ffffff !important; font-size: 2.8rem !important; font-weight: 700;}
h2, h3 {color: #e2e8f0 !important; font-weight: 600;}
.metric-card {background: rgba(99,102,241,0.15); padding: 1.5rem; border-radius: 15px; border: 1px solid rgba(99,102,241,0.3); transition: all 0.3s ease;}
.metric-card-green {background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3);}
.metric-card-red {background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3);}
.empty-placeholder {background: rgba(50,50,80,0.4); color: #94a3b8; padding: 2rem; border-radius: 15px; border: 2px dashed #6366f1; text-align: center;}
.stDataEditor {background: rgba(30,30,63,0.8);}
</style>
""", unsafe_allow_html=True)

# ==================== جدول فارغ تماماً ====================
st.markdown("# 📊 **لوحة تحكم المبيعات**")
st.markdown("### *ابدأ بإدخال بياناتك في الجدول أدناه*")

if 'products_df' not in st.session_state:
    st.session_state.products_df = pd.DataFrame(columns=[
        'product_name', 'price', 'cost', 'quantity_sold', 'stock'
    ])

# الجدول السلس والناعم
edited_df = st.data_editor(
    st.session_state.products_df,
    column_config={
        "product_name": st.column_config.TextColumn(
            "📦 اسم المنتج", 
            help="اسم المنتج بالكامل",
            required=True,
            width="medium"
        ),
        "price": st.column_config.NumberColumn(
            "💰 سعر البيع", 
            format="%.0f ج.م", 
            min_value=0,
            step=100,
            required=True
        ),
        "cost": st.column_config.NumberColumn(
            "💸 تكلفة الشراء", 
            format="%.0f ج.م", 
            min_value=0,
            step=100,
            required=True
        ),
        "quantity_sold": st.column_config.NumberColumn(
            "🛒 المباع", 
            min_value=0,
            step=1,
            help="عدد الوحدات المباعة"
        ),
        "stock": st.column_config.NumberColumn(
            "📊 المخزون", 
            min_value=0,
            step=1,
            help="الكمية المتبقية"
        )
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)

# تحديث البيانات بسلاسة
st.session_state.products_df = edited_df

# التحقق من وجود بيانات صحيحة
has_valid_data = len(edited_df) > 0 and (
    (edited_df['price'] > 0).sum() > 0 or 
    (edited_df['quantity_sold'] > 0).sum() > 0
)

df = edited_df.copy()

# ==================== التحليلات ====================
if has_valid_data:
    # حساب المؤشرات بسرعة
    df['revenue'] = pd.to_numeric(df['price'], errors='coerce') * pd.to_numeric(df['quantity_sold'], errors='coerce')
    df['cost_total'] = pd.to_numeric(df['cost'], errors='coerce') * pd.to_numeric(df['quantity_sold'], errors='coerce')
    df['profit'] = df['revenue'] - df['cost_total']
    df['profit_margin'] = (df['profit'] / df['revenue'].replace(0, np.nan) * 100).round(1)
    df['roi'] = ((df['profit'] / df['cost_total'].replace(0, np.nan)) * 100).round(1)
    
    # تنظيف البيانات
    df_display = df[df['revenue'] > 0].copy()
    
    # ==================== KPIs الناعمة ====================
    col1, col2, col3, col4 = st.columns(4, gap="1rem")
    
    total_revenue = df_display['revenue'].sum()
    total_profit = df_display['profit'].sum()
    total_sold = df_display['quantity_sold'].sum()
    avg_margin = df_display['profit_margin'].mean()
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>💰 الإيرادات</h3>
            <h2>{total_revenue:,.0f} ج.م</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card-green'>
            <h3>💵 الربح</h3>
            <h2>{total_profit:,.0f} ج.م</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>📦 المباع</h3>
            <h2>{total_sold:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>📊 هامش الربح</h3>
            <h2>{avg_margin:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== أفضل/أسوأ المنتجات ====================
    st.markdown("---")
    col1, col2 = st.columns(2, gap="2rem")
    
    with col1:
        st.markdown("### 🏆 **أفضل المنتجات**")
        if not df_display.empty:
            top_3 = df_display.nlargest(3, 'revenue')[['product_name', 'revenue', 'profit_margin']]
            st.dataframe(top_3.round(1).style.format({
                'revenue': '{:,.0f} ج.م',
                'profit_margin': '{:.1f}%'
            }).background_gradient(cmap='Greens'), use_container_width=True)
    
    with col2:
        st.markdown("### 📉 **أقل أداء**")
        if not df_display.empty:
            bottom_3 = df_display.nsmallest(3, 'revenue')[['product_name', 'revenue', 'profit_margin']]
            st.dataframe(bottom_3.round(1).style.format({
                'revenue': '{:,.0f} ج.م',
                'profit_margin': '{:.1f}%'
            }).background_gradient(cmap='Reds'), use_container_width=True)
    
    # ==================== الرسوم السلسة ====================
    col1, col2 = st.columns(2, gap="2rem")
    
    with col1:
        st.markdown("### 💹 **الإيرادات × الربح**")
        if len(df_display) > 0:
            fig1 = px.scatter(df_display, x='revenue', y='profit', 
                            size='quantity_sold', hover_name='product_name',
                            size_max=40, opacity=0.8,
                            title="كل نقطة = منتج")
            fig1.update_layout(
                font=dict(color="#e2e8f0", size=12),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown("### 📊 **هامش الربح**")
        if len(df_display) > 0:
            fig2 = px.bar(df_display.sort_values('profit_margin', ascending=True), 
                         x='profit_margin', y='product_name', 
                         orientation='h', opacity=0.8,
                         title="نسبة الربح (%)")
            fig2.update_layout(
                font=dict(color="#e2e8f0", size=12),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    
    # ==================== التقرير الشامل ====================
    st.markdown("### 📈 **تقرير كامل**")
    if len(df_display) > 0:
        report_df = df_display[['product_name', 'price', 'cost', 'quantity_sold', 
                               'revenue', 'profit', 'profit_margin', 'stock']].round(1)
        st.dataframe(report_df.style.format({
            'price': '{:,.0f} ج.م',
            'cost': '{:,.0f} ج.م',
            'revenue': '{:,.0f} ج.م',
            'profit': '{:,.0f} ج.م',
            'profit_margin': '{:.1f}%'
        }).background_gradient(subset=['profit_margin'], cmap='RdYlGn'), 
        use_container_width=True)

else:
    # ==================== العرض الفارغ الناعم ====================
    col1, col2, col3, col4 = st.columns(4, gap="1rem")
    
    with col1:
        st.markdown("""
        <div class='empty-placeholder'>
            <h3>💰 الإيرادات</h3>
            <h2>0 ج.م</h2>
            <p>ابدأ الإدخال</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='empty-placeholder'>
            <h3>💵 الربح</h3>
            <h2>0 ج.م</h2>
            <p>لا توجد بيانات</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='empty-placeholder'>
            <h3>📦 المبيعات</h3>
            <h2>0</h2>
            <p>انتظر التحليل</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='empty-placeholder'>
            <h3>📊 هامش الربح</h3>
            <h2>0%</h2>
            <p>ستظهر قريباً</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='empty-placeholder' style='height: 350px; display: flex; flex-direction: column; justify-content: center;'>
            <h3>💹 الرسوم البيانية</h3>
            <p>اضغط + في الجدول أعلاه</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='empty-placeholder' style='height: 350px; display: flex; flex-direction: column; justify-content: center;'>
            <h3>📊 التحليلات</h3>
            <p>ستظهر بعد إدخال البيانات</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== SIDEBAR الناعم ====================
with st.sidebar:
    st.markdown("## 🚀 **ابدأ الآن**")
    st.markdown("""
    ### 📝 **الخطوات:**
    1. **اضغط +** في الجدول أعلاه
    2. اكتب **اسم المنتج**
    3. أدخل **السعر** و**التكلفة**
    4. اكتب **المباع** و**المخزون**
    
    ✨ **التحليلات تتحدث فوراً!**
    """)
    
    if st.button("✨ **بيانات تجريبية**", use_container_width=True):
        st.session_state.products_df = pd.DataFrame({
            'product_name': ['iPhone 16 Pro', 'MacBook Pro', 'AirPods Pro 3'],
            'price': [45000, 78000, 12900],
            'cost': [32000, 55000, 8500],
            'quantity_sold': [25, 12, 45],
            'stock': [75, 38, 155]
        })
        st.rerun()
