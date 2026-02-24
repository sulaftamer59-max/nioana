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

# Luxury Dark Theme مع حقول فاتحة ✅
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    .main {background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);}
    .stApp {background-color: transparent;}
    
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background: linear-gradient(145deg, #f8fafc, #e2e8f0) !important;
        color: #1e293b !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 15px !important;
        padding: 15px 18px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
        border-radius: 15px !important;
        padding: 15px 30px !important;
        font-weight: 600 !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.6) !important;
    }
    
    h1 {color: #f1f5f9 !important; font-size: 3rem !important;}
    h2 {color: #e2e8f0 !important;}
    .card {background: rgba(26, 26, 46, 0.95); border-radius: 20px; padding: 2rem; margin: 1rem 0;}
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
        'dashboard': 'Dashboard'
    },
    'ar': {
        'title': 'سوق الفخامة 🇪🇬', 'register': 'تسجيل', 'login': 'دخول',
        'email': 'الإيميل', 'password': 'كلمة المرور', 'egp': 'جنيه', 'name': 'الاسم',
        'phone': 'الهاتف', 'address': 'العنوان', 'search_store': 'ابحث عن متجر...',
        'add_product': 'إضافة منتج', 'products': 'المنتجات', 'orders': 'الطلبات',
        'dashboard': 'لوحة التحكم'
    }
}

def get_text(key):
    return LANGUAGES[st.session_state.language][key]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_strong_password(password):
    return (len(password) >= 8 and 
            any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '!@#$%^&*()?' for c in password))

def is_valid_phone(phone):
    return bool(re.match(r"^01\d{9}$", phone))

# Sidebar
with st.sidebar:
    st.selectbox("🌐 Language", ["English 🇺🇸", "العربية 🇸🇦"], 
                index=0 if st.session_state.language == 'en' else 1,
                key="lang_select", on_change=lambda: setattr(st.session_state, 'language', 
                'en' if st.session_state.lang_select == "English 🇺🇸" else 'ar') or st.rerun())
    
    if st.session_state.current_user:
        st.info(f"👤 {st.session_state.current_user.get('store_name', 'User')}")
        if st.button("🚪 Logout"):
            for key in ['current_user', 'current_store', 'cart', 'show_user_type', 'temp_user']:
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
                    if is_strong_password(password):
                        if email not in st.session_state.data['users']:
                            st.session_state.data['users'][email] = {
                                'password': hash_password(password), 'type': None,
                                'name': '', 'store_name': ''
                            }
                            st.session_state.show_user_type = True
                            st.session_state.temp_user = email
                            st.success("✅ Account created! Choose your type.")
                            st.rerun()
                        else:
                            st.error("❌ Email exists!")
                    else:
                        st.error("❌ Weak password!")
                else:
                    st.error("❌ Fill all fields!")
        
        # User type selection
        if st.session_state.show_user_type and st.session_state.temp_user:
            st.markdown("---")
            st.markdown("""
                <div style='text-align:center; padding:3rem'>
                    <h1 style='background:linear-gradient(45deg,#3b82f6,#1d4ed8);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>
                    🎯 Choose Account Type
                    </h1>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="card">🏪<h2>Store Owner</h2><p>Manage your store</p></div>', unsafe_allow_html=True)
                if st.button("✅ Store Owner", use_container_width=True):
                    email = st.session_state.temp_user
                    st.session_state.data['users'][email]['type'] = 'owner'
                    st.session_state.current_user = st.session_state.data['users'][email]
                    st.session_state.show_user_type = False
                    st.rerun()
            
            with col2:
                st.markdown('<div class="card">🛒<h2>Buyer</h2><p>Shop easily</p></div>', unsafe_allow_html=True)
                if st.button("✅ Buyer", use_container_width=True):
                    email = st.session_state.temp_user
                    st.session_state.data['users'][email]['type'] = 'buyer'
                    st.session_state.current_user = st.session_state.data['users'][email]
                    st.session_state.show_user_type = False
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
    if not st.session_state.current_user.get('store_name'):
        st.session_state.current_user['store_name'] = st.text_input("Store Name")
        if st.button("Save Store"):
            st.session_state.data['stores'][st.session_state.current_user['store_name']] = {
                'products': [], 'orders': []
            }
            st.rerun()
        return
    
    store_name = st.session_state.current_user['store_name']
    store = st.session_state.data['stores'].get(store_name, {'products': [], 'orders': []})
    
    tab1, tab2 = st.tabs(["➕ Add Product", "📦 Products"])
    
    with tab1:
        with st.form("product_form"):
            col1, col2 = st.columns(2)
            with col1: name = st.text_input("Product Name")
            with col2: price = st.number_input("Price EGP", min_value=0.0)
            qty = st.number_input("Quantity", min_value=1)
            
            if st.form_submit_button("Add"):
                store['products'].append({'name': name, 'price': price, 'qty': qty})
                st.success("✅ Added!")
                st.rerun()
    
    with tab2:
        if store['products']:
            st.dataframe(pd.DataFrame(store['products']))

def buyer_dashboard():
    search = st.text_input("🔍 Search Stores")
    stores = list(st.session_state.data['stores'].keys())
    
    for store in stores:
        if st.button(f"🏪 {store}"):
            st.session_state.current_store = store
            st.rerun()
    
    if st.session_state.current_store:
        store = st.session_state.data['stores'][st.session_state.current_store]
        for product in store['products']:
            if st.button(f"🛒 {product['name']} - {product['price']} EGP"):
                st.session_state.cart.setdefault(st.session_state.current_store, {})[product['name']] = 1
                st.success("Added to cart!")

if __name__ == "__main__":
    main()
