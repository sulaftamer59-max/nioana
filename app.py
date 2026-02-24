# استبدل قسم الـ CSS بالكود ده في بداية الملف:

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* الخلفية الداكنة الفخمة */
    .main {background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);}
    .stApp {background-color: transparent;}
    
    /* حقول الكتابة فاتحة ومريحة */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        background: linear-gradient(145deg, #f8fafc, #e2e8f0) !important;
        color: #1e293b !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 15px !important;
        padding: 15px 18px !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        background: linear-gradient(145deg, #ffffff, #f1f5f9) !important;
    }
    
    /* الأزرار الفخمة */
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #1d4ed8, #1e40af) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px 30px !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 16px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(59, 130, 246, 0.6) !important;
        background: linear-gradient(45deg, #1d4ed8, #1e40af, #1e3a8a) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* العناوين */
    h1 {color: #f1f5f9 !important; font-size: 3rem !important; font-weight: 700; text-shadow: 0 2px 10px rgba(0,0,0,0.3);}
    h2 {color: #e2e8f0 !important; font-size: 2rem !important; font-weight: 600;}
    h3 {color: #cbd5e1 !important; font-size: 1.5rem !important; font-weight: 600;}
    
    /* البطاقات */
    .card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.95), rgba(30, 30, 63, 0.9)) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3) !important;
    }
    
    /* الرسائل */
    .stSuccess > div {background: linear-gradient(135deg, #10b981, #059669); color: white; border-radius: 12px;}
    .stError > div {background: linear-gradient(135deg, #ef4444, #dc2626); color: white; border-radius: 12px;}
    
    /* الجدول */
    .stDataFrame {background-color: rgba(26, 26, 46, 0.9) !important; border-radius: 15px !important;}
    
    /* الشريط الجانبي */
    .css-1d391kg {background: linear-gradient(180deg, rgba(10,10,26,0.95) 0%, rgba(26,26,46,0.95) 100%) !important;}
    
    /* تحسين المسافات */
    .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)
