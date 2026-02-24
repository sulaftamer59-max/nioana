import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import plotly.express as px
import re

# Page config
st.set_page_config(
    page_title="Luxury Market EG 🇪🇬",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Luxury Dark Theme ✅ خلفية داكنة + محتوى فاتح واضح
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* خلفية داكنة فخمة */
    .main {background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);}
    .stApp {background-color: transparent;}
    
    /* النصوص والعناوين فاتحة واضحة */
    h1, h2, h3, h4, h5, h6 {color: #ffffff !important; font-family: 'Poppins', sans-serif !important;}
    .stMarkdown {color: #e2e8f0 !important;}
    
    /* حقول الكتابة فاتحة */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: linear-gradient(145deg, #f8fafc, #e2e8f0) !important;
        color: #1e293b !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 15px !important;
        padding: 15px 18px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* الأزرار الفخمة */
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px 30px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.6) !important;
    }
    
    /* البطاقات */
    .card {
        background: rgba(30, 30, 63, 0.9) !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
    }
    
    /* الجداول */
    .stDataFrame {background-color: rgba(30, 30, 63, 0.9) !important; color: #ffffff !important;}
    
    /* الرسائل */
    .stSuccess > div {background: linear-gradient(135deg, #10b981, #059669); color: white;}
    .stError > div {background: linear-gradient(135deg, #ef4444, #dc2626); color: white;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'data': {'users': {}, 'stores': {}},
        'current_user': None,
        'current_store': None,
        'cart': {},
        'language': 'en',
        'show_user_type': False,
        'temp_user': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Languages
LANGUAGES = {
    'en': {
        'title': 'Luxury Market EG 🇪🇬', 'register': 'Register', 'login': 'Login',
        'email': 'Email', 'password': 'Password', 'egp': 'EGP', 'name': 'Full Name',
        'phone': 'Phone (01XXXXXXXX)', 'address': 'Address', 'search_store': 'Search Store...',
        'add_product': 'Add Product', 'products': 'Products', 'orders': 'Orders',
        'dashboard': 'Dashboard', 'store_name': 'Store Name'
    },
    'ar': {
        'title': 'سوق الفخامة 🇪🇬', 'register': 'تسجيل', 'login': 'دخول',
        'email': 'الإيميل', 'password': 'كلمة المرور', 'egp': 'جنيه', 'name': 'الاسم',
        'phone': 'الهاتف', 'address': 'العنوان', 'search_store': 'ابحث عن متجر...',
        'add_product': 'إضافة منتج', 'products': 'المنتجات', 'orders': 'الطلبات',
        'dashboard': 'لوحة التحكم', 'store_name': 'اسم المتجر'
    }
}

def get_text(key):
    return LANGUAGES[st.session_state.language][key]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_phone(phone):
    return bool(re.match(r"^01\d{9}$", phone))

# Sidebar ✅ إصلاح مشكلة اللغة
with st.sidebar:
    selected_lang = st.selectbox("🌐 Language", ["English 🇺🇸", "العربية 🇸🇦"], 
                                index=0 if st.session_state.language == 'en' else 1)
    if selected_lang == "English 🇺🇸":
        st.session_state.language = 'en'
    else:
        st.session_state.language = 'ar'
    
    if st.session_state.current_user:
        st.success(f"👤 {st.session_state.current_user.get('store_name', 'User')}")
        if st.button("🚪 Logout"):
            for key in ['current_user', 'current_store', 'cart', 'show_user_type', 'temp_user']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Main App
def main():
    if st.session_state.current_user:
        if st.session_state.current_user['type'] == 'owner':
            owner_dashboard()
        else:
            buyer_dashboard()
    else:
        auth_page()

def auth_page():
    st.markdown(f"# {get_text('title')}")
    
    tab1, tab2 = st.tabs([f"👤 {get_text('register')}", f"🔐 {get_text('login')}"])
    
    with tab1:
        with st.form("register"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input(get_text('email'))
            with col2:
                password = st.text_input(get_text('password'), type="password")
            
            if st.form_submit_button(get_text('register')):
                if email and password:
                    if email not in st.session_state.data['users']:
                        st.session_state.data['users'][email] = {
                            'password': hash_password(password), 
                            'type': None,
                            'name': '', 
                            'store_name': '',
                            'email': email  # ✅ حفظ الإيميل
                        }
                        st.session_state.show_user_type = True
                        st.session_state.temp_user = email
                        st.success("✅ Account created! Choose your type.")
                        st.rerun()
                    else:
                        st.error("❌ Email exists!")
                else:
                    st.error("❌ Fill all fields!")
        
        # User type selection ✅ محسن
        if st.session_state.show_user_type and st.session_state.temp_user:
            st.markdown("---")
            st.markdown("""
                <div style='text-align:center; padding:3rem'>
                    <h1 style='background:linear-gradient(45deg,#3b82f6,#1d4ed8);-webkit-background-clip:text;-webkit-text-fill-color:transparent; font-size:3.5rem'>
                    🎯 Choose Account Type
                    </h1>
                    <p style='color:#e2e8f0; font-size:1.3rem'>اختر نوع حسابك</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2, gap="2rem")
            with col1:
                st.markdown("""
                    <div class="card" style='text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center'>
                        <div style='font-size:5rem'>🏪</div>
                        <h2>Store Owner</h2>
                        <p style='color:#cbd5e1'>إدارة متجرك الخاص ✨<br>إضافة منتجات<br>تحليل المبيعات</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("✅ **I am Store Owner**", use_container_width=True):
                    email = st.session_state.temp_user
                    st.session_state.data['users'][email]['type'] = 'owner'
                    st.session_state.current_user = st.session_state.data['users'][email]
                    st.session_state.show_user_type = False
                    st.session_state.temp_user = None
                    st.rerun()
            
            with col2:
                st.markdown("""
                    <div class="card" style='text-align:center; height:400px; display:flex; flex-direction:column; justify-content:center'>
                        <div style='font-size:5rem'>🛒</div>
                        <h2>Buyer</h2>
                        <p style='color:#cbd5e1'>تسوق بسهولة ✨<br>إضافة للسلة<br>طلب سريع</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("✅ **I am Buyer**", use_container_width=True):
                    email = st.session_state.temp_user
                    st.session_state.data['users'][email]['type'] = 'buyer'
                    st.session_state.current_user = st.session_state.data['users'][email]
                    st.session_state.show_user_type = False
                    st.session_state.temp_user = None
                    st.rerun()
    
    with tab2:
        with st.form("login"):
            email = st.text_input(get_text('email'), key="login_email")
            password = st.text_input(get_text('password'), type="password", key="login_pass")
            
            if st.form_submit_button(get_text('login')):
                if (email in st.session_state.data['users'] and 
                    st.session_state.data['users'][email]['password'] == hash_password(password)):
                    st.session_state.current_user = st.session_state.data['users'][email]
                    st.rerun()
                else:
                    st.error("❌ Wrong credentials!")

def owner_dashboard():
    # ✅ إصلاح مشكلة اسم المتجر
    st.markdown(f"# 🏪 {get_text('dashboard')} - {st.session_state.current_user.get('store_name', 'No Store')}")
    
    if not st.session_state.current_user.get('store_name'):
        st.markdown("### 🚀 **أول مرة؟ أنشئ متجرك الآن!**")
        col1, col2 = st.columns([2, 1])
        with col1:
            store_name = st.text_input(get_text('store_name'), placeholder="اسم متجرك الجميل...")
        with col2:
            st.info("💡 اجعل اسم متجرك مميز!")
        
        if st.button("✅ **إنشاء المتجر**", use_container_width=True):
            if store_name:
                st.session_state.current_user['store_name'] = store_name
                st.session_state.data['stores'][store_name] = {
                    'owner': st.session_state.current_user['email'],
                    'owner_email': st.session_state.current_user['email'],
                    'products': [], 
                    'orders': [],
                    'inventory': {}
                }
                st.success(f"✅ تم إنشاء متجر **{store_name}** بنجاح!")
                st.rerun()
            else:
                st.error("❌ اكتب اسم المتجر أولاً!")
        return
    
    # لو المتجر موجود ✅
    store_name = st.session_state.current_user['store_name']
    if store_name not in st.session_state.data['stores']:
        st.session_state.data['stores'][store_name] = {
            'owner': st.session_state.current_user['email'],
            'products': [], 
            'orders': []
        }
    
    store = st.session_state.data['stores'][store_name]
    
    tab1, tab2, tab3 = st.tabs([get_text('add_product'), get_text('products'), get_text('orders')])
    
    with tab1:
        st.markdown("### ➕ " + get_text('add_product'))
        with st.form("product_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم المنتج")
                price = st.number_input("السعر EGP", min_value=0.0, format="%.2f")
            with col2:
                qty = st.number_input("الكمية", min_value=1)
                desc = st.text_area("الوصف", height=100)
            
            if st.form_submit_button("➕ إضافة المنتج", use_container_width=True):
                store['products'].append({
                    'id': len(store['products']) + 1,
                    'name': name, 
                    'price': price, 
                    'qty': qty,
                    'desc': desc,
                    'stock': qty
                })
                st.success("✅ تم إضافة المنتج!")
                st.rerun()
    
    with tab2:
        if store['products']:
            df = pd.DataFrame(store['products'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📦 لا توجد منتجات بعد!")
    
    with tab3:
        if store['orders']:
            st.dataframe(pd.DataFrame(store['orders']))
        else:
            st.info("📬 لا توجد طلبات بعد!")

def buyer_dashboard():
    st.markdown("### 🔍 " + get_text('search_store'))
    search = st.text_input("ابحث عن متجر...", placeholder="اكتب اسم المتجر...")
    
    stores = list(st.session_state.data['stores'].keys())
    if search:
        stores = [s for s in stores if search.lower() in s.lower()]
    
    if stores:
        st.markdown("### 🏪 المتاجر المتاحة:")
        for store_name in stores:
            if st.button(f"🏪 **{store_name}**", key=f"enter_store_{store_name}", use_container_width=True):
                st.session_state.current_store = store_name
                st.rerun()
    else:
        st.info("🔍 لا توجد متاجر بهذا الاسم")
    
    # عرض المتجر المختار
    if st.session_state.current_store:
        store = st.session_state.data['stores'][st.session_state.current_store]
        st.markdown(f"# 🏪 {st.session_state.current_store}")
        
        if store['products']:
            cols = st.columns(3)
            for i, product in enumerate(store['products']):
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="card">
                            <h3>{product['name']}</h3>
                            <p>{product.get('desc', '')[:60]}...</p>
                            <p><strong style='color:#3b82f6'>{product['price']:,} {get_text('egp')}</strong></p>
                            <p>الكمية: {product['stock']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("🛒 إضافة للسلة", key=f"add_{product['id']}"):
                        if 'cart' not in st.session_state:
                            st.session_state.cart = {}
                        st.session_state.cart.setdefault(st.session_state.current_store, {})[product['id']] = \
                        st.session_state.cart.get(st.session_state.current_store, {}).get(product['id'], 0) + 1
                        st.success(f"✅ تم إضافة {product['name']}")

if __name__ == "__main__":
    main()
