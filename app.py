import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Business Dashboard", layout="wide")

# CSS بسيط وناعم
st.markdown("""
<style>
.main {background: linear-gradient(135deg, #0c0c1a 0%, #1a1a2e 100%);}
h1 {color: #ffffff !important; font-size: 2.5rem !important;}
h2, h3 {color: #e2e8f0 !important;}
.metric {background: rgba(99,102,241,0.2); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;}
.empty {background: rgba(50,50,80,0.5); color: #94a3b8; padding: 2rem; border-radius: 10px; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.title("📊 لوحة تحكم المبيعات")

# جدول فارغ تماماً
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['product_name', 'price', 'cost', 'quantity_sold', 'stock'])

# الجدول الرئيسي
edited_df = st.data_editor(
    st.session_state.df,
    column_config={
        "product_name": st.column_config.TextColumn("اسم المنتج"),
        "price": st.column_config.NumberColumn("سعر البيع (ج.م)", format="%.0f"),
        "cost": st.column_config.NumberColumn("تكلفة (ج.م)", format="%.0f"),
        "quantity_sold": st.column_config.NumberColumn("المباع"),
        "stock": st.column_config.NumberColumn("المخزون")
    },
    num_rows="dynamic",
    use_container_width=True
)

st.session_state.df = edited_df
df = st.session_state.df

# التحقق من البيانات
has_data = len(df) > 0 and df[['price', 'quantity_sold']].sum().sum() > 0

if has_data:
    # الحسابات
    df['revenue'] = df['price'] * df['quantity_sold']
    df['profit'] = df['revenue'] - (df['cost'] * df['quantity_sold'])
    df['margin'] = (df['profit'] / df['revenue'].replace(0, 1) * 100).round(1)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='metric'>
            <h3>الإيرادات</h3>
            <h2>{df['revenue'].sum():,.0f} ج.م</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric'>
            <h3>الربح</h3>
            <h2>{df['profit'].sum():,.0f} ج.م</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric'>
            <h3>المباع</h3>
            <h2>{df['quantity_sold'].sum():,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='metric'>
            <h3>هامش الربح</h3>
            <h2>{df['margin'].mean():.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # أفضل المنتجات
    st.subheader("🏆 أفضل المنتجات")
    top = df.nlargest(3, 'revenue')[['product_name', 'revenue', 'profit']]
    st.dataframe(top.round())
    
    # الرسوم
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.scatter(df, x='revenue', y='profit', size='quantity_sold', 
                         hover_name='product_name', title="الإيرادات × الربح")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(df.sort_values('margin'), x='margin', y='product_name', 
                     orientation='h', title="هامش الربح")
        st.plotly_chart(fig2, use_container_width=True)
    
    # الجدول الكامل
    st.subheader("📋 التقرير الكامل")
    st.dataframe(df.round(0))

else:
    # العرض الفارغ
    col1, col2, col3, col4 = st.columns(4)
    for col in [col1, col2, col3, col4]:
        col.markdown("""
        <div class='empty'>
            <h3>--</h3>
            <p>لا توجد بيانات</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='empty'>
        <h2>🚀 ابدأ الآن</h2>
        <p>1. اضغط + في الجدول أعلاه<br>
           2. أضف منتجاتك<br>
           3. التحليلات ستظهر تلقائياً</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar بسيط
with st.sidebar:
    st.header("🎯 الاستخدام")
    st.markdown("""
    1. **اضغط +** في الجدول
    2. **املأ البيانات**
    3. **التحليلات جاهزة!**
    """)
    
    if st.button("🧪 بيانات تجريبية"):
        st.session_state.df = pd.DataFrame({
            'product_name': ['آيفون', 'ماك بوك', 'ايربودز'],
            'price': [45000, 78000, 12900],
            'cost': [32000, 55000, 8500],
            'quantity_sold': [25, 12, 45],
            'stock': [75, 38, 155]
        })
        st.rerun()
