import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

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

# ==================== MAIN APP ====================
st.markdown("# 📊 **BusinessPro Dashboard**")
st.markdown("### *تحليل بياناتك الخاصة - ارفع ملفك الآن!*")

# ==================== UPLOAD & INPUT SECTION ====================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📁 **ارفع ملف Excel/CSV الخاص بك**")
    uploaded_file = st.file_uploader(
        "اختر ملف البيانات (Excel أو CSV)", 
        type=['csv', 'xlsx'],
        help="الملف يجب يحتوي على: التاريخ | المبيعات | عدد الطلبات | العملاء"
    )

with col2:
    st.markdown("### ⌨️ **أو أدخل البيانات يدوياً**")
    manual_data = st.text_area(
        "أدخل بياناتك هنا (تاريخ,المبيعات,الطلبات,العملاء):",
        placeholder="2025-01-01,50000,25,15\n2025-01-02,62000,32,18",
        height=100
    )

# ==================== DATA PROCESSING ====================
@st.cache_data
def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # تنظيف الأسماء
            df.columns = df.columns.str.strip().str.lower()
            
            # تحديد الأعمدة المهمة
            date_col = next((col for col in ['date', 'تاريخ', 'التاريخ'] if col in df.columns), None)
            revenue_col = next((col for col in ['revenue', 'مبيعات', 'المبيعات', 'sales'] if col in df.columns), None)
            orders_col = next((col for col in ['orders', 'طلبات', 'الطلبات'] if col in df.columns), None)
            customers_col = next((col for col in ['customers', 'عملاء', 'العملاء'] if col in df.columns), None)
            
            if date_col and revenue_col:
                df['date'] = pd.to_datetime(df[date_col])
                df['revenue'] = pd.to_numeric(df[revenue_col], errors='coerce')
                if orders_col:
                    df['orders'] = pd.to_numeric(df[orders_col], errors='coerce')
                if customers_col:
                    df['customers'] = pd.to_numeric(df[customers_col], errors='coerce')
                
                return df[['date', 'revenue', 'orders', 'customers']].dropna()
        except:
            st.error("❌ مشكلة في قراءة الملف")
    return None

@st.cache_data
def process_manual_data(text_data):
    if text_data.strip():
        try:
            lines = text_data.strip().split('\n')
            data = []
            for line in lines:
                parts = line.split(',')
                if len(parts) >= 2:
                    data.append({
                        'date': pd.to_datetime(parts[0].strip()),
                        'revenue': float(parts[1].strip()),
                        'orders': float(parts[2].strip()) if len(parts) > 2 else 0,
                        'customers': float(parts[3].strip()) if len(parts) > 3 else 0
                    })
            return pd.DataFrame(data)
        except:
            st.error("❌ تنسيق البيانات غير صحيح")
    return None

# معالجة البيانات
df = None
if uploaded_file is not None:
    df = process_uploaded_file(uploaded_file)
elif manual_data.strip():
    df = process_manual_data(manual_data)

# ==================== DISPLAY DATA ====================
if df is not None and len(df) > 0:
    st.success(f"✅ تم تحليل **{len(df)}** سجل بنجاح!")
    
    # عرض عينة من البيانات
    st.markdown("### 📋 **عينة من بياناتك**")
    st.dataframe(df.head(), use_container_width=True)
    
    # ==================== METRICS ====================
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = df['revenue'].sum()
    total_orders = df['orders'].sum() if 'orders' in df else 0
    total_customers = df['customers'].sum() if 'customers' in df else 0
    avg_revenue = df['revenue'].mean()
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>💰 إجمالي المبيعات</h3>
            <h1>EGP {total_revenue:,.0f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>📦 إجمالي الطلبات</h3>
            <h1>{total_orders:,.0f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>👥 إجمالي العملاء</h3>
            <h1>{total_customers:,.0f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>📊 متوسط المبيعات اليومي</h3>
            <h1>EGP {avg_revenue:,.0f}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== CHARTS ====================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💹 **تطور المبيعات**")
        fig1 = px.line(df.sort_values('date'), x='date', y='revenue',
                      title="المبيعات عبر الزمن")
        fig1.update_layout(font=dict(color="#e2e8f0"))
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        if 'orders' in df.columns:
            st.markdown("### 📦 **عدد الطلبات**")
            fig2 = px.bar(df.tail(30).sort_values('date'), x='date', y='orders')
            fig2.update_layout(font=dict(color="#e2e8f0"))
            st.plotly_chart(fig2, use_container_width=True)
    
    # ==================== TREND ANALYSIS ====================
    if len(df) > 1:
        st.markdown("### 📈 **تحليل الاتجاهات**")
        
        recent = df.tail(7)  # آخر 7 أيام
        growth = ((recent['revenue'].iloc[-1] - recent['revenue'].iloc[0]) / recent['revenue'].iloc[0]) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("نمو المبيعات الأسبوعي", f"{growth:.1f}%")
        with col2:
            st.metric("أعلى يوم مبيعات", f"EGP {df['revenue'].max():,.0f}")
        with col3:
            st.metric("متوسط يومي", f"EGP {df['revenue'].mean():,.0f}")

else:
    st.info("📤 **ارفع ملف Excel/CSV أو أدخل بياناتك يدوياً في المربع المجاور**")
    
    st.markdown("""
    ### 📋 **تنسيق البيانات المطلوب:**
    ```
    التاريخ,المبيعات,الطلبات,العملاء
    2025-01-01,50000,25,15
    2025-01-02,62000,32,18
    2025-01-03,45000,22,12
    ```
    **أو ارفع ملف Excel/CSV يحتوي على نفس الأعمدة**
    """)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## ⚙️ **إعدادات التحليل**")
    
    st.markdown("### 📊 **نوع الرسم البياني**")
    chart_type = st.selectbox("اختر الرسم:", ["خطي", "عمودي"])
    
    st.markdown("### ⏱️ **فترة التحليل**")
    period = st.selectbox("الفترة:", ["كل البيانات", "آخر 30 يوم", "آخر 7 أيام"])
