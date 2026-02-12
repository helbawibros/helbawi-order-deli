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
st.set_page_config(page_title="Helbawi Admin Pro", layout="centered")

# --- CSS لتصميم اللمبات والأزرار ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    
    /* تصميم اللمبات */
    .status-container {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-bottom: 20px;
        padding: 10px;
        background-color: #1c2333;
        border-radius: 15px;
        border: 1px solid #2d3748;
    }
    .led-light {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .led-green {
        background-color: #00ff00;
        box-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00 inset;
    }
    .led-red {
        background-color: #ff0000;
        box-shadow: 0 0 5px #ff0000;
        opacity: 0.4;
    }
    .led-tooltip {
        position: relative;
        display: inline-block;
    }
    
    /* تصميم الأزرار والعناوين */
    .main-header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 15px; margin-bottom: 20px; border-bottom: 4px solid #fca311;}
    div.stButton > button { width: 100%; background-color: #fca311 !important; color: #1E3A8A !important; font-weight: bold; height: 50px; border-radius: 10px; font-size: 18px; }
    .wa-button { background-color: #25d366 !important; color: white !important; padding: 12px; border-radius: 10px; text-align: center; display: block; text-decoration: none; font-weight: bold; margin-top: 10px; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

# --- دوال الاتصال والبيانات ---

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw_json = st.secrets["gcp_service_account"]["json_data"].strip()
    creds = Credentials.from_service_account_info(json.loads(raw_json, strict=False), scopes=scope)
    return gspread.authorize(creds)

# 1. جلب حالة المندوبين (للمبات)
def get_active_status(all_delegates):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        
        # محاولة فتح شيت النشاط
        try:
            ws = sheet.worksheet("Active_Users")
            data = ws.get_all_records()
        except:
            return {} # إذا الشيت مش موجود، نرجع فارغ

        status_map = {}
        current_time = datetime.now()
        
        for row in data:
            try:
                # التأكد من اسم العمود حسب ملفك (سواء عربي أو انجليزي)
                u_name = row.get('المندوب') or row.get('User') or row.get('name')
                u_time = row.get('آخر_ظهور') or row.get('Last_Seen') or row.get('time')
                
                last_seen = datetime.strptime(str(u_time), "%Y-%m-%d %H:%M")
                diff = (current_time - last_seen).total_seconds() / 60
                
                # إذا ظهر خلال آخر 15 دقيقة يعتبر أونلاين
                status_map[str(u_name).strip()] = diff < 15
            except:
                continue
        return status_map
    except:
        return {}

# 2. رسم اللمبات
def render_status_lights(delegates_list):
    status_map = get_active_status(delegates_list)
    
    html_code = '<div class="status-container">'
    for rep in delegates_list:
        is_active = status_map.get(rep.strip(), False)
        color_class = "led-green" if is_active else "led-red"
        # العنوان يظهر فقط عند تمرير الماوس (title attribute)
        html_code += f'<div class="led-light {color_class}" title="{rep}"></div>'
    html_code += '</div>'
    
    st.markdown(html_code, unsafe_allow_html=True)

# 3. جلب رقم الهاتف
def get_phone_number(rep_name):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        ws_data = sheet.worksheet("البيانات")
        all_data = ws_data.get_all_values()
        for row in all_data:
            if row[0].strip() == rep_name.strip():
                return str(row[1]).strip()
        return None
    except: return None

# 4. صناعة PDF
def generate_order_pdf(rep_name, items_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, txt=f"Helbawi Bros Order: {rep_name}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(20, 10, "#", 1, 0, 'C', 1)
    pdf.cell(120, 10, "Item", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Qty", 1, 1, 'C', 1)
    
    for i, item in enumerate(items_list, 1):
        # تنظيف النص للعربية (FPDF Basic لا يدعم العربية، نستخدم اللاتيني أو تنظيف)
        clean_name = str(item['name']).encode('latin-1', 'ignore').decode('latin-1') 
        pdf.cell(20, 10, str(i), 1, 0, 'C')
        pdf.cell(120, 10, clean_name[:40], 1, 0, 'L')
        pdf.cell(40, 10, str(item['qty']), 1, 1, 'C')
        
    return pdf.output(dest='S').encode('latin-1')

# 5. تصديق الطلب (دفعات)
def finalize_and_update(rep_name, items):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        ws = sheet.worksheet(rep_name.strip())
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        rows = [[now_str, i['name'], i['qty'], "تم التصديق", "جردة سيارة"] for i in items]
        
        chunk_size = 15
        for i in range(0, len(rows), chunk_size):
            ws.append_rows(rows[i:i + chunk_size])
            time.sleep(0.5)
        return True
    except: return False

# 6. جلب قائمة المندوبين (فلتر)
def get_delegates_list():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        all_sheets = sheet.worksheets()
        excluded = ["طلبات", "الذمم", "بيانات المندوبين", "عاجل", "الرئيسية", "البيانات", "الاسعار", "Sheet1", "Active_Users"]
        return [s.title for s in all_sheets if s.title not in excluded and " " in s.title.strip()]
    except: return []

# تحميل الأصناف
@st.cache_data(ttl=60)
def load_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0/gviz/tq?tqx=out:csv&sheet=طلبات"
        df = pd.read_csv(url, header=None).dropna(how='all').iloc[:, :5]
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except: return None

df = load_data()

# إدارة الجلسة
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cust_name' not in st.session_state: st.session_state.cust_name = ""

# --- الصفحة الرئيسية ---
if df is not None:
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>لوحة تحكم حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        # 1. شريط اللمبات (رادار النشاط)
        delegates = get_delegates_list()
        if delegates:
            render_status_lights(delegates)
        
        # 2. اختيار المندوب
        st.markdown("<p style='text-align:right; font-weight:bold;'>👤 اختر المندوب للعمل:</p>", unsafe_allow_html=True)
        st.session_state.cust_name = st.selectbox("المندوب", ["-- اختر --"] + delegates, label_visibility="collapsed")

        # 3. الأقسام
        for c in df['cat'].unique():
            if st.button(f"📦 {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        if st.session_state.cart:
            st.divider()
            if st.button("🛒 مراجعة الطلبية"):
                st.session_state.page = 'review'
                st.rerun()

    # --- صفحة التفاصيل ---
    elif st.session_state.page == 'details':
        if st.button("🏠 عودة"): st.session_state.page = 'home'; st.rerun()
        cat_df = df[df['cat'] == st.session_state.sel_cat]
        for _, row in cat_df.iterrows():
            key = f"q_{row['name']}"
            val = st.text_input(row['name'], key=key, value=st.session_state.cart.get(key, {}).get('qty', ""))
            if val: st.session_state.cart[key] = {'name': row['name'], 'qty': val}
        if st.button("🛒 حفظ ومراجعة"): st.session_state.page = 'review'; st.rerun()

    # --- صفحة المراجعة (PDF + WhatsApp + تصديق) ---
    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>تثبيت الطلب وإرساله</h1></div>', unsafe_allow_html=True)
        st.info(f"المندوب: {st.session_state.cust_name}")
        
        final_items = []
        for i, (k, v) in enumerate(st.session_state.cart.items(), 1):
            st.write(f"**{i}.** {v['name']} -> **{v['qty']}**")
            final_items.append(v)

        # زر التصديق الأساسي
        if st.button("🚀 تصديق الطلب (تحديث الجرد)"):
            if finalize_and_update(st.session_state.cust_name, final_items):
                st.success("✅ تم تحديث الجرد في الإكسل!")
        
        st.markdown("---")
        
        # منطقة PDF وواتساب
        phone = get_phone_number(st.session_state.cust_name)
        
        if phone:
            # 1. إنشاء وتحميل PDF
            pdf_bytes = generate_order_pdf(st.session_state.cust_name, final_items)
            st.download_button(
                label="📄 تحميل فاتورة PDF",
                data=pdf_bytes,
                file_name=f"Order_{st.session_state.cust_name}.pdf",
                mime="application/pdf"
            )
            
            # 2. زر الواتساب
            msg = f"مرحباً سيد {st.session_state.cust_name}،\nتم تصديق طلبيتك ({len(final_items)} صنف).\nيرجى استلام الملف المرفق."
            wa_link = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-button">📲 إرسال للمندوب (WhatsApp)</a>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ رقم هاتف المندوب غير موجود في شيت 'البيانات'.")

    if st.button("🏠 الرئيسية", key="home_btn"): 
        st.session_state.page = 'home'
        st.rerun()
