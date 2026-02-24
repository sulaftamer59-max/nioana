import streamlit as st
import pandas as pd
import hashlib
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
import re

# Page config
st.set_page_config(
    page_title="Luxury Market EG 🇪🇬",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Luxury Dark Theme - Eye-friendly & Elegant
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #16213e 100%);}
    .stApp {background-color: transparent;}
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1e1e3f !important;
        color: #e8e8f0 !important;
        border-radius: 12px;
        border: 1px solid #2a2a5a;
        padding: 12px;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 500;
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #e8e8f0 !important;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
    }
    
    /* Metrics */
    .metric-container {background: linear-gradient(135deg, #2a2a5a, #3a3a6a); border-radius: 15px; padding: 1.5rem;}
    
    /* Cards */
    .card {background: rgba(30, 30, 63, 0.8); border-radius: 15px; padding: 1.5rem; border: 1px solid #3a3a6a;}
    </style>
""", unsafe_allow_html=True)

# Multi-language support
if 'language' not in st.session_state:
    st.session_state.language = 'en'

LANGUAGES = {
    'en': {
        'title': 'Luxury Market EG 🇪🇬',
        'register': 'Register New Account',
        'login': 'Login',
        'email': 'Email',
        'password': 'Password',
        'strong_pwd_msg': '✅ Strong password! Requirements: 8+ chars, Uppercase, Lowercase, Numbers, Special chars',
        'weak_pwd_msg': '❌ Weak password! Need: 8+ chars, Uppercase, Lowercase, Numbers, Special chars',
        'user_type': 'Account Type',
        'owner': 'Store Owner 🏪',
        'buyer': 'Buyer 🛒',
        'dashboard': 'Dashboard 📊',
        'add_product': 'Add Product ➕',
        'products': 'Products 📦',
        'inventory': 'Inventory 📋',
        'orders': 'Orders 🧾',
        'analytics': 'Analytics 📈',
        'search_store': 'Search Store... 🔍',
        'suggested_stores': 'Suggested Stores',
        'add_to_cart': 'Add to Cart 🛒',
        'checkout': 'Checkout 💳',
        'name': 'Full Name',
        'phone': 'Phone (Egypt: 01XXXXXXXX)',
        'address': 'Detailed Address',
        'egp': 'EGP',
        'price': 'Price',
        'quantity': 'Quantity',
        'stock': 'Stock',
        'store_name': 'Store Name'
    },
    'ar': {
        'title': 'سوق الفخامة مصر 🇪🇬',
        'register': 'إنشاء حساب جديد',
        'login': 'تسجيل الدخول',
        'email': 'البريد الإلكتروني',
        'password': 'كلمة المرور',
        'strong_pwd_msg': '✅ كلمة مرور قوية! المتطلبات: 8+ حرف، كبير، صغير، أرقام، رموز خاصة',
        'weak_pwd_msg': '❌ كلمة مرور ضعيفة! يجب: 8+ حرف، كبير، صغير، أرقام، رموز خاصة',
        'user_type': 'نوع الحساب',
        'owner': 'مالك متجر 🏪',
        'buyer': 'مشتري 🛒',
        'dashboard': 'لوحة التحكم 📊',
        'add_product': 'إضافة منتج ➕',
        'products': 'المنتجات 📦',
        'inventory': 'المخزون 📋',
        'orders': 'الطلبات 🧾',
        'analytics': 'الإحصائيات 📈',
        'search_store': 'ابحث عن متجر... 🔍',
        'suggested_stores': 'متاجر مقترحة',
        'add_to_cart': 'إضافة للسلة 🛒',
        'checkout': 'إتمام الشراء 💳',
        'name': 'الاسم الكامل',
        'phone': 'الهاتف (مصر: 01XXXXXXXX)',
        'address': 'العنوان التفصيلي',
        'egp': 'جنيه',
        'price': 'السعر',
        'quantity': 'الكمية',
        'stock': 'المخزون',
        'store_name': 'اسم المتجر'
    }
}

def get_text(key):
    return LANGUAGES[st.session_state.language][key]

# Data storage
@st.cache_data(ttl=3600)
def init_data():
    return {
        'users': {},
        'stores': {},
        'orders': {}
    }

if 'data' not in st.session_state:
    st.session_state.data = init_data()
    st.session_state.current_user = None
    st.session_state.current_store = None
    st.session_state.cart = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def is_valid_egypt_phone(phone: str) -> bool:
    return bool(re.match(r"^01[0-9]{9}$", phone))

# Sidebar Language Switcher
with st.sidebar:
    st.markdown("🌐 **Language / اللغة**")
    lang = st.selectbox("Select Language", ["English 🇺🇸", "العربية 🇸🇦"], 
                       index=0 if st.session_state.language == 'en' else 1,
                       key="lang_switch")
    if lang == "English 🇺🇸":
        st.session_state.language = 'en'
    else:
        st.session_state.language = 'ar'

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
    st.markdown("### ✨ Welcome to Luxury Market Egypt")
    
    tab1, tab2 = st.tabs(["👤 " + get_text('register'), "🔐 " + get_text('login')])
    
    with tab1:
        with st.form("register_form"):
            st.markdown("### " + get_text('register'))
            email = st.text_input(get_text('email'), placeholder="user@example.com")
            password = st.text_input(get_text('password'), type="password", placeholder="Strong Password123!")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.form_submit_button(get_text('register'), use_container_width=True):
                    if is_strong_password(password):
                        st.success(get_text('strong_pwd_msg'))
                        if email not in st.session_state.data['users']:
                            st.session_state.data['users'][email] = {
                                'password': hash_password(password),
                                'type': None,  # Will be set next
                                'name': '',
                                'phone': '',
                                'store_name': ''
                            }
                            st.session_state.current_user = st.session_state.data['users'][email]
                            st.rerun()
                        else:
                            st.error("❌ Email already registered!")
                    else:
                        st.error(get_text('weak_pwd_msg'))
            
            if st.session_state.current_user and st.session_state.current_user['type'] is None:
                st.markdown("### 🎯 " + get_text('user_type'))
                if st.radio(get_text('user_type'), ['owner', 'buyer'], key="user_type_select") == 'owner':
                    st.session_state.current_user['type'] = 'owner'
                    name = st.text_input("Store Owner Name")
                    store_name = st.text_input(get_text('store_name'))
                    if st.button("✅ Complete Owner Setup", use_container_width=True):
                        st.session_state.current_user['name'] = name
                        st.session_state.data['stores'][store_name] = {
                            'owner': email,
                            'products': [],
                            'orders': [],
                            'inventory': {}
                        }
                        st.session_state.current_user['store_name'] = store_name
                        st.rerun()
                else:
                    st.session_state.current_user['type'] = 'buyer'
                    st.rerun()
    
    with tab2:
        with st.form("login_form"):
            email = st.text_input(get_text('email'), placeholder="user@example.com", key="login_email")
            password = st.text_input(get_text('password'), type="password", key="login_pass")
            
            if st.form_submit_button(get_text('login'), use_container_width=True):
                if email in st.session_state.data['users'] and \
                   st.session_state.data['users'][email]['password'] == hash_password(password):
                    st.session_state.current_user = st.session_state.data['users'][email]
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password!")

def owner_dashboard():
    st.markdown(f"# 🏪 {get_text('dashboard')} - {st.session_state.current_user['store_name']}")
    
    store_name = st.session_state.current_user['store_name']
    store_data = st.session_state.data['stores'][store_name]
    
    tab1, tab2, tab3, tab4 = st.tabs([
        get_text('add_product'), 
        get_text('products'), 
        get_text('orders'), 
        get_text('analytics')
    ])
    
    with tab1:
        st.markdown("### ➕ " + get_text('add_product'))
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Product Name")
                category = st.text_input("Category")
                price = st.number_input("Price (EGP)", min_value=0.0, format="%.2f")
            with col2:
                description = st.text_area("Description", height=80)
                quantity = st.number_input(get_text('quantity'), min_value=1)
            
            if st.form_submit_button("➕ Add Product", use_container_width=True):
                product = {
                    'id': len(store_data['products']) + 1,
                    'name': name,
                    'category': category,
                    'price': price,
                    'description': description,
                    'quantity': quantity,
                    'stock': quantity,
                    'sales': []
                }
                store_data['products'].append(product)
                store_data['inventory'][name] = quantity
                st.success("✅ Product added successfully!")
                st.rerun()
    
    with tab2:
        st.markdown("### 📦 " + get_text('products'))
        if store_data['products']:
            df = pd.DataFrame(store_data['products'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 No products yet. Add some from the first tab!")
    
    with tab3:
        st.markdown("### 🧾 " + get_text('orders'))
        if store_data['orders']:
            df_orders = pd.DataFrame(store_data['orders'])
            st.dataframe(df_orders, use_container_width=True)
        else:
            st.info("📬 No orders yet!")
    
    with tab4:
        st.markdown("### 📈 " + get_text('analytics'))
        if store_data['products']:
            fig_revenue = px.bar(
                x=[p['name'] for p in store_data['products']],
                y=[p['price'] * len(p['sales']) for p in store_data['products']],
                title="Revenue by Product",
                labels={'x': 'Product', 'y': 'Revenue (EGP)'}
            )
            st.plotly_chart(fig_revenue, use_container_width=True)

def buyer_dashboard():
    st.markdown(f"# 🛒 {get_text('title')}")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(get_text('search_store'), placeholder=get_text('search_store'))
    
    with col2:
        if st.button("🔍 Search", use_container_width=True):
            st.rerun()
    
    # Suggested stores
    st.markdown("### ✨ " + get_text('suggested_stores'))
    suggested_stores = [name for name in st.session_state.data['stores'].keys()]
    
    if search_query:
        filtered_stores = [s for s in suggested_stores if search_query.lower() in s.lower()]
    else:
        filtered_stores = suggested_stores[:3]
    
    for store_name in filtered_stores:
        if st.button(f"🏪 {store_name}", key=f"enter_{store_name}"):
            st.session_state.current_store = store_name
            st.rerun()
    
    if st.session_state.current_store:
        show_store_page()

def show_store_page():
    store_name = st.session_state.current_store
    store_data = st.session_state.data['stores'][store_name]
    
    st.markdown(f"# 🏪 {store_name}")
    
    # Products grid
    cols = st.columns(3)
    for i, product in enumerate(store_data['products']):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
                <h4>{product['name']}</h4>
                <p><strong>{product['category']}</strong></p>
                <p>{product['description'][:50]}...</p>
                <p><strong style='color: #667eea; font-size: 1.2em;'>
                {product['price']:,} {get_text('egp')}
                </strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🛒 {get_text('add_to_cart')}", key=f"add_{product['id']}"):
                if 'cart' not in st.session_state:
                    st.session_state.cart = {}
                if product['id'] not in st.session_state.cart:
                    st.session_state.cart[product['id']] = 1
                else:
                    st.session_state.cart[product['id']] += 1
                st.success(f"✅ {product['name']} added to cart!")
    
    # Cart & Checkout
    if st.session_state.cart:
        st.markdown("### 🛒 Shopping Cart")
        total = 0
        cart_items = []
        for product_id, qty in st.session_state.cart.items():
            product = next(p for p in store_data['products'] if p['id'] == product_id)
            subtotal = product['price'] * qty
            total += subtotal
            cart_items.append({'product': product['name'], 'qty': qty, 'price': product['price'], 'total': subtotal})
        
        st.dataframe(pd.DataFrame(cart_items), use_container_width=True)
        st.markdown(f"### 💰 **Total: {total:,.2f} {get_text('egp')}**")
        
        if st.button(get_text('checkout'), use_container_width=True):
            with st.form("checkout_form"):
                name = st.text_input(get_text('name'))
                phone = st.text_input(get_text('phone'), placeholder="01XXXXXXXXX")
                address = st.text_area(get_text('address'), placeholder="Detailed address...")
                
                if st.form_submit_button("💳 Complete Order", use_container_width=True):
                    if is_valid_egypt_phone(phone):
                        order = {
                            'id': len(store_data['orders']) + 1,
                            'customer': {'name': name, 'phone': phone, 'address': address},
                            'items': cart_items,
                            'total': total,
                            'date': datetime.now().isoformat(),
                            'status': 'pending'
                        }
                        store_data['orders'].append(order)
                        st.session_state.cart = {}
                        st.success("✅ Order placed successfully! Owner will contact you.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Egyptian phone number! Use format: 01XXXXXXXXX")

# Logout
st.sidebar.markdown("---")
if st.session_state.current_user:
    if st.sidebar.button("🚪 Logout"):
        st.session_state.current_user = None
        st.session_state.current_store = None
        st.session_state.cart = {}
        st.rerun()

if __name__ == "__main__":
    main()
