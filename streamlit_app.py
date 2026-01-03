import streamlit as st
import pandas as pd
import random
from datetime import datetime
import requests

# --- 1. إعدادات التنسيق والهوية ---
LOGO_FILE = "IMG_6470.jpeg"

st.set_page_config(
    page_title="شركة حلباوي إخوان", 
    layout="centered", 
    page_icon=LOGO_FILE
)

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@600;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }}
    
    /* إخفاء تعليمات الموبايل المزعجة */
    div[data-testid="InputInstructions"], div[data-baseweb="helper-text"] {{ display: none !important; }}

    /* جعل اللوغو يظهر بشكل دائري أو بحواف ناعمة ليختفي السواد */
    .logo-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: -40px;
        margin-bottom: 20px;
        width: 100%;
    }}
    .logo-container img {{
        border-radius: 20px; /* لتنعيم الحواف السوداء المربعة */
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); /* ظل خفيف ليعطيه جمالية */
        border: 2px solid #1E3A8A;
    }}

    .header-box {{ background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}}
    .return-header-box {{ background-color: #B22222; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 20px;}}
    
    /* ... (باقي كود التنسيق للفواتير كما هو) ... */
    </style>
    """, unsafe_allow_html=True)

# --- عرض اللوغو في المنتصف بحجم 140 ---
# هذا السطر سيجبر اللوغو على البقاء في المنتصف دائماً وبحجم معتدل
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
st.image(LOGO_FILE, width=140)
st.markdown('</div>', unsafe_allow_html=True)

# --- 2. البيانات والوظائف (نفس كودك السابق دون تغيير حرف) ---
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
GID_PRICES = "339292430"
GID_DATA = "0"
GID_CUSTOMERS = "155973706" 

@st.cache_data(ttl=60)
def load_rep_customers(rep_name):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_CUSTOMERS}"
        df = pd.read_csv(url)
        rep_df = df[df.iloc[:, 0].astype(str).str.strip() == rep_name.strip()]
        return {f"{row.iloc[1]} ({row.iloc[2]})": row.iloc[1] for _, row in rep_df.iterrows()}
    except: return {}

def get_next_invoice_number():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_DATA}"
        df = pd.read_csv(url)
        if 'رقم الفاتوره' in df.columns:
            valid_nums = pd.to_numeric(df['رقم الفاتوره'], errors='coerce').dropna()
            if not valid_nums.empty: return str(int(valid_nums.max()) + 1)
        return "1001"
    except: return str(random.randint(10000, 99999))

@st.cache_data(ttl=60)
def load_products_from_excel():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_PRICES}"
        df_p = pd.read_csv(url)
        df_p.columns = [c.strip() for c in df_p.columns]
        return pd.Series(df_p.iloc[:, 1].values, index=df_p.iloc[:, 0]).to_dict()
    except: return {"⚠️ خطأ": 0.0}

PRODUCTS = load_products_from_excel()

def send_to_google_sheets(vat, total_pre, inv_no, customer, representative, date_time, is_ret=False):
    url = "https://script.google.com/macros/s/AKfycbzi3kmbVyg_MV1Nyb7FwsQpCeneGVGSJKLMpv2YXBJR05v8Y77-Ub2SpvViZWCCp1nyqA/exec"
    prefix = "(مرتجع) " if is_ret else ""
    data = {"vat_value": vat, "total_before": total_pre, "invoice_no": inv_no, "cust_name": f"{prefix}{customer}", "rep_name": representative, "date_full": date_time}
    try:
        requests.post(url, data=data, timeout=10)
        return True
    except: return False

USERS = {"عبد الكريم حوراني": "9900", "محمد الحسيني": "8822", "علي دوغان": "5500", "عزات حلاوي": "6611", "علي حسين حلباوي": "4455", "محمد حسين حلباوي": "3366", "احمد حسين حلباوي": "7722", "علي محمد حلباوي": "6600"}

# إدارة الحالة
for key in ['logged_in', 'page', 'temp_items', 'confirmed', 'receipt_view', 'is_sent', 'is_return', 'widget_id']:
    if key not in st.session_state:
        if key == 'temp_items': st.session_state[key] = []
        elif key == 'widget_id': st.session_state[key] = 0
        elif key == 'page': st.session_state[key] = 'login'
        else: st.session_state[key] = False

def convert_ar_nav(text):
    n_map = {'٠':'0','١':'1','٢':'2','٣':'3','٤':'4','٥':'5','٦':'6','٧':'7','٨':'8','٩':'9'}
    return "".join(n_map.get(c, c) for c in text)

# --- الواجهات ---
if not st.session_state.logged_in:
    st.markdown('<div class="header-box"><h1>🔐 دخول المندوبين</h1></div>', unsafe_allow_html=True)
    user_sel = st.selectbox("إختر اسمك", ["-- اختر --"] + list(USERS.keys()))
    pwd = st.text_input("كلمة السر", type="password")
    if st.button("دخول", use_container_width=True):
        if USERS.get(user_sel) == pwd:
            st.session_state.logged_in, st.session_state.user_name, st.session_state.page = True, user_sel, 'home'
            st.rerun()

elif st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h2>شركة حلباوي إخوان</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;"><h3>أهلاً بك {st.session_state.user_name}</h3><p style="color:green; font-weight:bold; font-size:18px;">ببركة الصلاة على محمد وآل محمد</p></div>', unsafe_allow_html=True)
    col_inv, col_ret = st.columns(2)
    with col_inv:
        if st.button("📝 فاتورة جديدة", use_container_width=True, type="primary"):
            st.session_state.page, st.session_state.temp_items, st.session_state.confirmed, st.session_state.is_return = 'order', [], False, False
            st.session_state.inv_no = get_next_invoice_number()
            st.rerun()
    with col_ret:
        if st.button("🔄 تسجيل مرتجع", use_container_width=True):
            st.session_state.page, st.session_state.temp_items, st.session_state.confirmed, st.session_state.is_return = 'order', [], False, True
            st.session_state.inv_no = get_next_invoice_number()
            st.rerun()

# ... (باقي الكود يكمل هنا بنفس الترتيب السابق) ...
