import os
import time
import json
os.environ['TZ'] = 'Asia/Beirut' 
import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF 

# 1. إعدادات الصفحة
st.set_page_config(page_title="إدارة حلباوي برو", layout="centered")

# --- دالة جلب رقم الهاتف من صفحة البيانات ---
def get_phone_from_sheet(delegate_name):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw_json = st.secrets["gcp_service_account"]["json_data"].strip()
        creds = Credentials.from_service_account_info(json.loads(raw_json, strict=False), scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        
        # فتح صفحة البيانات والبحث عن الرقم في العمود B
        ws_data = sheet.worksheet("البيانات")
        records = ws_data.get_all_values()
        for row in records:
            if row[0].strip() == delegate_name.strip():
                return str(row[1]).strip()
        return None
    except:
        return None

# --- دالة إنشاء الـ PDF المرتب ---
def create_pdf_file(delegate_name, items_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Order: {delegate_name}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    # الجدول (123 | الصنف | العدد)
    pdf.cell(20, 10, "#", 1, 0, 'C')
    pdf.cell(130, 10, "Item Name", 1, 0, 'C')
    pdf.cell(40, 10, "Qty", 1, 1, 'C')
    
    for i, item in enumerate(items_list, 1):
        pdf.cell(20, 10, str(i), 1, 0, 'C')
        pdf.cell(130, 10, str(item['name'])[:50], 1, 0, 'L')
        pdf.cell(40, 10, str(item['qty']), 1, 1, 'C')
        
    return pdf.output(dest='S').encode('latin-1')

# --- دالة جلب قائمة المندوبين (تحديث فوري + فلتر ذكي) ---
def get_clean_delegates():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw_json = st.secrets["gcp_service_account"]["json_data"].strip()
        creds = Credentials.from_service_account_info(json.loads(raw_json, strict=False), scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        all_sh = sheet.worksheets()
        
        excluded = ["طلبات", "الذمم", "بيانات المندوبين", "عاجل", "الرئيسية", "البيانات", "الاسعار", "Sheet1"]
        # شرط الكلمتين (وجود مسافة) لفلترة الصفحات الإدارية
        return [s.title for s in all_sh if s.title not in excluded and " " in s.title.strip()]
    except: return []

# --- دالة الإرسال بنظام الدفعات (لمنع التقطيع) ---
def send_in_batches(delegate_name, items):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw_json = st.secrets["gcp_service_account"]["json_data"].strip()
        creds = Credentials.from_service_account_info(json.loads(raw_json, strict=False), scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        ws = sheet.worksheet(delegate_name.strip())
        
        rows = [[datetime.now().strftime("%Y-%m-%d %H:%M"), i['name'], i['qty'], "بانتظار التصديق"] for i in items]
        chunk_size = 20
        for i in range(0, len(rows), chunk_size):
            ws.append_rows(rows[i:i + chunk_size])
            time.sleep(0.5)
        return True
    except: return False

# 2. تحميل الأصناف
@st.cache_data(ttl=60)
def load_items():
    try:
        url = f"https://docs.google.com/spreadsheets/d/1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0/gviz/tq?tqx=out:csv&sheet=طلبات"
        df = pd.read_csv(url, header=None).dropna(how='all').iloc[:, :5]
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except: return None

df_items = load_items()

# 3. التصميم الجمالي
st.markdown("""<style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .main-header { background-color: #1E3A8A; text-align: center; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-bottom: 5px solid #fca311;}
    div.stButton > button { width: 100%; background-color: #fca311 !important; color: #1E3A8A !important; font-weight: bold; height: 55px; border-radius: 12px; font-size: 20px; }
    .wa-button { background-color: #25d366 !important; color: white !important; padding: 15px; border-radius: 12px; text-align: center; display: block; text-decoration: none; font-weight: bold; margin-top: 10px; font-size: 20px;}
    </style>""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cust_name' not in st.session_state: st.session_state.cust_name = ""

# --- المنطق الرئيسي ---
if df_items is not None:
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>نظام إدارة الطلبيات</h1></div>', unsafe_allow_html=True)
        
        # اختيار المندوب
        delegates = get_clean_delegates()
        st.session_state.cust_name = st.selectbox("👤 المندوب المختار:", ["-- اختر مندوب --"] + delegates)

        # عرض الأقسام
        for c in df_items['cat'].unique():
            if st.button(f"📦 قسم {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        if st.session_state.cart:
            st.divider()
            if st.button("🛒 مراجعة الطلب الحالي"):
                st.session_state.page = 'review'
                st.rerun()

    elif st.session_state.page == 'details':
        if st.button("🏠 عودة"): st.session_state.page = 'home'; st.rerun()
        cat_df = df_items[df_items['cat'] == st.session_state.sel_cat]
        for _, row in cat_df.iterrows():
            key = f"q_{row['name']}"
            val = st.text_input(row['name'], key=key, value=st.session_state.cart.get(key, {}).get('qty', ""))
            if val: st.session_state.cart[key] = {'name': row['name'], 'qty': val}
        if st.button("🛒 حفظ ومراجعة"): st.session_state.page = 'review'; st.rerun()

    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>تأكيد الطلبية</h1></div>', unsafe_allow_html=True)
        st.info(f"المندوب: {st.session_state.cust_name}")
        
        final_list = []
        for i, (k, v) in enumerate(st.session_state.cart.items(), 1):
            st.write(f"**{i}.** {v['name']} --- العدد: **{v['qty']}**")
            final_list.append(v)

        if st.button("🚀 1. تصديق الطلب في جوجل شيت"):
            if send_in_batches(st.session_state.cust_name, final_list):
                st.success("✅ تم التحديث بنجاح!")

        st.divider()
        # --- قسم الـ PDF والواتساب (يظهر دائماً عند المراجعة) ---
        st.subheader("📲 إرسال الطلبية للمندوب")
        
        phone_num = get_phone_from_sheet(st.session_state.cust_name)
        
        if phone_num:
            # تجهيز الـ PDF
            pdf_bytes = create_pdf_file(st.session_state.cust_name, final_list)
            
            # زر التحميل
            st.download_button(
                label="📥 1. تحميل الطلبية PDF",
                data=pdf_bytes,
                file_name=f"Order_{st.session_state.cust_name}.pdf",
                mime="application/pdf",
                key="pdf_download_btn"
            )
            
            # زر الواتساب
            msg_text = f"أهلاً سيد {st.session_state.cust_name}، تم تصديق طلبيتك رقم ({datetime.now().strftime('%H:%M')}). يرجى تحميل المرفق."
            wa_link = f"https://api.whatsapp.com/send?phone={phone_num}&text={urllib.parse.quote(msg_text)}"
            st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-button">💬 2. إرسال عبر واتساب المندوب</a>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ لم يتم العثور على رقم هاتف لهذا المندوب في صفحة 'البيانات'.")

    if st.button("🏠 العودة للرئيسية", key="nav_home"): 
        st.session_state.page = 'home'
        st.rerun()
