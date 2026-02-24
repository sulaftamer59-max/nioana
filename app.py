import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import re

# Page config
st.set_page_config(
    page_title="Luxury Market EG 🇪🇬",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Luxury Theme ✅ خلفية داكنة + محتوى فاتح واضح
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* خلفية داكنة فخمة */
    .main {background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);}
    .stApp {background-color: transparent;}
    
    /* كل النصوص فاتحة واضحة */
    h1, h2, h3, h4, h5, h6 {color: #ffffff !important; font-family: 'Poppins', sans-serif !important;}
    p, div, span {color: #e2e8f0 !important;}
    
    /* حقول الكتابة فاتحة */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        background: linear-gradient(145deg, #f8fafc, #e2e8f0) !important;
        color: #1e293b !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 15px !important;
        padding: 15px 18px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* الأزرار */
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
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.6) !important;
    }
    
    /* البطاقات */
    .card {
        background: rgba(30, 30, 63, 0.95) !important;
        color: #ffffff !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
    }
    
    /* الجداول */
    .stDataFrame {background-color: rgba(30, 30, 63, 0.9) !important; color: #ffffff !important;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state ✅ مضمون
if 'data' not in st.session_state:
    st.session_state.data = {'users': {}, 'stores': {}}
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'current_store' not in st.session_state:
    st.session_state.current_store = None
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Languages ✅ مختصر
LANGUAGES = {
    'en': {
        'title': 'Luxury Market EG 🇪🇬', 'register': 'Register', 'login': 'Login',
        'email': 'Email', 'password': 'Password', 'egp': 'EGP',
        'store_name': 'Store Name', 'add_product': 'Add Product', 
        'products': 'Products', 'orders': 'Orders', 'search_store': 'Search Store...'
    },
    'ar': {
        'title': 'سوق الفخامة 🇪🇬', 'register': 'تسجيل', 'login': 'دخول',
        'email': 'الإيميل', 'password': 'كلمة المرور', 'egp': 'جنيه',
        'store_name': 'اسم المتجر', 'add_product': 'إضافة منتج', 
        'products': 'المنتجات', 'orders': 'الطلبات', 'search_store': 'ابحث عن متجر...'
    }
}

def get_text(key):
    return LANGUAGES[st.session_state.language][key]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Sidebar ✅ مبسط
with st.sidebar:
    st.selectbox("🌐 اللغة", ["English 🇺🇸", "العربية 🇸🇦"], 
                index=0 if st.session_state.language == 'en' else 1,
                key="lang_key", on_change=lambda: st.session_state.update(language='en' if st.session_state.lang_key=="English 🇺🇸" else 'ar') or st.rerun())
    
    if st.session_state.current_user:
        st.success(f"👤 {st.session_state.current_user.get('store_name', 'User')}")
        if st.button("🚪 Logout"):
            st.session_state.current_user = None
            st.session_state.current_store = None
            st.session_state.cart = {}
            st.rerun()

# Main App
def main():
    if st.session_state.current_user:
        if st.session_state.current_user.get('type') == 'owner':
            owner_dashboard()
        else:
            buyer_dashboard()
    else:
        auth_page()

def auth_page():
    st.markdown(f"# {get_text('title')}")
    st.markdown("### ✨ Welcome to Luxury Shopping")
    
    tab1, tab2 = st.tabs([f"👤 {get_text('register')}", f"🔐 {get_text('login')}"])
    
    with tab1:
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input(get_text('email'), placeholder="user@example.com")
            with col2:
                password = st.text_input(get_text('password'), type="password", placeholder="any password")
            
            if st.form_submit_button(f"✅ {get_text('register')}"):
                if email and password:
                    if email not in st.session_state.data['users']:
                        st.session_state.data['users'][email] = {
                            'password': hash_password(password),
                            'type': None,
                            'store_name': ''
                        }
                        st.session_state.temp_email = email
                        st.success("✅ Account created! Choose account type.")
                        st.rerun()
                    else:
                        st.error("❌ Email already exists!")
                else:
                    st.error("❌ Please fill all fields!")
        
        # ✅ اختيار نوع الحساب
        if 'temp_email' in st.session_state:
            st.markdown("---")
            st.markdown("### 🎯 **Choose Your Account Type**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🏪 **Store Owner**", use_container_width=True):
                    email = st.session_state.temp_email
                    st.session_state.data['users'][email]['type'] = 'owner'
                    st.session_state.current_user = st.session_state.data['users'][email]
                    del st.session_state.temp_email
                    st.rerun()
            
            with col2:
                if st.button("🛒 **Buyer**", use_container_width=True):
                    email = st.session_state.temp_email
                    st.session_state.data['users'][email]['type'] = 'buyer'
                    st.session_state.current_user = st.session_state.data['users'][email]
                    del st.session_state.temp_email
                    st.rerun()
    
    with tab2:
        with st.form("login_form"):
            email = st.text_input(get_text('email'), key="login_email")
            password = st.text_input(get_text('password'), type="password", key="login_pass")
            
            if st.form_submit_button(f"🔑 {get_text('login')}"):
                if (email in st.session_state.data['users'] and 
                    st.session_state.data['users'][email]['password'] == hash_password(password)):
                    st.session_state.current_user = st.session_state.data['users'][email]
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials!")

def owner_dashboard():
    st.markdown(f"# 🏪 Owner Dashboard")
    
    # ✅ إنشاء المتجر إذا مش موجود
    if not st.session_state.current_user.get('store_name'):
        st.markdown("### 🚀 **Create Your Store**")
        store_name = st.text_input("Store Name", placeholder="Enter beautiful store name...")
        
        col1, col2 = st.columns([3,1])
        with col2:
            st.info("💡 Make it unique!")
        
        if st.button("✅ Create Store", use_container_width=True):
            if store_name.strip():
                st.session_state.current_user['store_name'] = store_name.strip()
                st.session_state.data['stores'][store_name.strip()] = {
                    'owner': st.session_state.current_user.get('email', email),
                    'products': [],
                    'orders': []
                }
                st.success(f"✅ Store '{store_name}' created successfully!")
                st.rerun()
            else:
                st.error("❌ Store name cannot be empty!")
        return
    
    # ✅ لو المتجر موجود
    store_name = st.session_state.current_user['store_name']
    store = st.session_state.data['stores'].get(store_name, {'products': [], 'orders': []})
    
    tab1, tab2 = st.tabs(["➕ Add Product", "📦 Products"])
    
    with tab1:
        with st.form("product_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name")
                price = st.number_input("Price (EGP)", min_value=0.01)
            with col2:
                quantity = st.number_input("Quantity", min_value=1)
            
            if st.form_submit_button("➕ Add Product"):
                store['products'].append({
                    'name': name,
                    'price': price,
                    'quantity': quantity
                })
                st.success("✅ Product added!")
                st.rerun()
    
    with tab2:
        if store['products']:
            st.dataframe(pd.DataFrame(store['products']))
        else:
            st.info("📦 No products yet!")

def buyer_dashboard():
    st.markdown("### 🔍 Find Stores")
    search = st.text_input("Search stores...", placeholder="Type store name...")
    
    # ✅ عرض كل المتاجر
    stores = list(st.session_state.data['stores'].keys())
    if stores:
        for store_name in stores:
            if st.button(f"🏪 {store_name}", key=f"store_{store_name}"):
                st.session_state.current_store = store_name
                st.rerun()
    else:
        st.info("🏪 No stores available yet!")
    
    # عرض المتجر المختار
    if st.session_state.current_store:
        store = st.session_state.data['stores'][st.session_state.current_store]
        st.markdown(f"## 🏪 {st.session_state.current_store}")
        
        for product in store['products']:
            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"**{product['name']}** - {product['price']:,} EGP")
            with col2:
                if st.button("🛒 Add", key=f"add_{product['name']}"):
                    st.success("✅ Added to cart!")
    else:
        st.info("👆 Click any store to browse products!")

if __name__ == "__main__":
    main()
