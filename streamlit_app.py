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
from fpdf import FPDF # مكتبة صناعة الـ PDF

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام حلباوي المطور", layout="centered")

# --- دالة جلب رقم المندوب من صفحة البيانات ---
def get_delegate_phone(delegate_name):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw_json = st.secrets["gcp_service_account"]["json_data"].strip()
        creds = Credentials.from_service_account_info(json.loads(raw_json, strict=False), scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        
        # الوصول لصفحة البيانات
        data_sheet = sheet.worksheet("البيانات")
        records = data_sheet.get_all_values() # جلب كل البيانات
        
        for row in records:
            if row[0].strip() == delegate_name.strip(): # البحث في العمود A
                return str(row[1]).strip() # إرجاع الرقم من العمود B
        return None
    except:
        return None

# --- دالة إنشاء ملف الـ PDF ---
def create_pdf(delegate_name, items):
    pdf = FPDF()
    pdf.add_page()
    # إضافة خط يدعم العربية (اختياري) أو الاكتفاء بالإنجليزية حالياً للسرعة
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Order for: {delegate_name}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    # الجدول
    pdf.cell(20, 10, "#", 1)
    pdf.cell(120, 10, "Item Name", 1)
    pdf.cell(40, 10, "Qty", 1)
    pdf.ln()
    
    for i, item in enumerate(items, 1):
        pdf.cell(20, 10, str(i), 1)
        pdf.cell(120, 10, item['name'][:40], 1) # قص الاسم إذا كان طويلاً جداً
        pdf.cell(40, 10, str(item['qty']), 1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1')

# --- دالة الربط مع جوجل شيت (نظام الدفعات) ---
def send_to_google_sheets(delegate_name, items_list):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw_json = st.secrets["gcp_service_account"]["json_data"].strip()
        creds = Credentials.from_service_account_info(json.loads(raw_json, strict=False), scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        worksheet = sheet.worksheet(delegate_name.strip())
        
        rows = [[datetime.now().strftime("%Y-%m-%d %H:%M"), i['name'], i['qty'], "بانتظار التصديق"] for i in items_list]
        worksheet.append_rows(rows)
        return True
    except:
        return False

# --- دالة جلب قائمة المندوبين ---
def get_delegates_list():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw_json = st.secrets["gcp_service_account"]["json_data"].strip()
        creds = Credentials.from_service_account_info(json.loads(raw_json, strict=False), scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        all_sheets = sheet.worksheets()
        excluded = ["طلبات", "الذمم", "بيانات المندوبين", "عاجل", "الرئيسية", "البيانات", "الاسعار"]
        return [s.title for s in all_sheets if s.title not in excluded and " " in s.title.strip()]
    except: return []

# 2. تحميل البيانات الأصناف
@st.cache_data(ttl=60)
def load_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0/gviz/tq?tqx=out:csv&sheet=طلبات"
        df = pd.read_csv(url, header=None).dropna(how='all').iloc[:, :5]
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except: return None

df = load_data()

# 3. CSS
st.markdown("""<style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .main-header { background-color: #1E3A8A; text-align: center; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    div.stButton > button { width: 100%; background-color: #fca311 !important; color: #1E3A8A !important; font-weight: bold; height: 50px; border-radius: 10px; }
    .wa-button { background-color: #25d366 !important; color: white !important; padding: 15px; border-radius: 10px; text-align: center; display: block; text-decoration: none; font-weight: bold; margin-top: 10px;}
    </style>""", unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cust_name' not in st.session_state: st.session_state.cust_name = ""

# --- الصفحة الرئيسية ---
if df is not None:
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>لوحة تحكم الإدارة</h1></div>', unsafe_allow_html=True)
        
        delegates = get_delegates_list()
        st.session_state.cust_name = st.selectbox("👤 اختر المندوب:", ["-- اختر --"] + delegates)

        for c in df['cat'].unique():
            if st.button(f"📦 قسم {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        if st.session_state.cart:
            st.divider()
            if st.button("🛒 مراجعة الطلبية"):
                st.session_state.page = 'review'
                st.rerun()

    # --- صفحة التفاصيل (نفس الكود السابق) ---
    elif st.session_state.page == 'details':
        if st.button("🏠 عودة"): st.session_state.page = 'home'; st.rerun()
        cat_df = df[df['cat'] == st.session_state.sel_cat]
        for _, row in cat_df.iterrows():
            key = f"q_{row['name']}"
            val = st.text_input(row['name'], key=key)
            if val: st.session_state.cart[key] = {'name': row['name'], 'qty': val}
        if st.button("🛒 حفظ ومراجعة"): st.session_state.page = 'review'; st.rerun()

    # --- صفحة المراجعة (هنا الذكاء) ---
    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>تثبيت وإرسال</h1></div>', unsafe_allow_html=True)
        
        final_list = []
        for i, (k, v) in enumerate(st.session_state.cart.items(), 1):
            st.write(f"{i}. {v['name']} -> {v['qty']}")
            final_list.append(v)

        if st.button("🚀 1. تحديث الجرد في الإكسل"):
            if send_to_google_sheets(st.session_state.cust_name, final_list):
                st.success("تم التحديث!")

        # --- زر الـ PDF والواتساب ---
        st.divider()
        phone = get_delegate_phone(st.session_state.cust_name)
        
        if phone:
            # إنشاء الـ PDF
            pdf_data = create_pdf(st.session_state.cust_name, final_list)
            
            # زر التحميل (PDF)
            st.download_button(
                label="📥 تحميل طلبية PDF",
                data=pdf_data,
                file_name=f"Order_{st.session_state.cust_name}.pdf",
                mime="application/pdf"
            )
            
            # رابط الواتساب التلقائي
            msg = f"تحية طيبة، مرفق طلبية المندوب: {st.session_state.cust_name}\nعدد الأصناف: {len(final_list)}"
            wa_url = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-button">💬 إرسال إشعار للمندوب (واتساب)</a>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ لم نجد رقم هاتف لهذا المندوب في صفحة البيانات (عمود B)")
