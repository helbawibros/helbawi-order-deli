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
st.set_page_config(page_title="Helbawi Admin", layout="centered")

# --- CSS (التصميم: لمبات + أزرار خضراء) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    
    /* تنسيق اللمبات */
    .status-container {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 15px;
        padding: 10px;
        background-color: #1c2333;
        border-radius: 12px;
        border: 1px solid #30363d;
    }
    .bulb {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 10px;
        border: 2px solid rgba(255,255,255,0.2);
        cursor: help;
        transition: transform 0.2s;
    }
    .bulb:hover { transform: scale(1.1); }
    .on { background-color: #00e676; box-shadow: 0 0 10px #00e676; } /* أخضر مضوي */
    .off { background-color: #b71c1c; opacity: 0.5; } /* أحمر باهت */

    /* تنسيق الأزرار */
    .main-header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 15px; margin-bottom: 20px; border-bottom: 4px solid #fca311;}
    
    /* زر التصديق (برتقالي/أحمر) */
    div.stButton > button { width: 100%; font-weight: bold; height: 50px; border-radius: 10px; font-size: 18px; }
    
    /* زر الواتساب (مخصص) */
    .wa-btn { 
        background-color: #25d366; 
        color: white !important; 
        padding: 12px; 
        border-radius: 8px; 
        text-align: center; 
        display: block; 
        text-decoration: none; 
        font-weight: bold; 
        font-size: 18px; 
        margin-top: 10px;
        border: 1px solid #1da851;
    }
    .wa-btn:hover { opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# --- دوال الاتصال والبيانات ---

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    raw_json = st.secrets["gcp_service_account"]["json_data"].strip()
    creds = Credentials.from_service_account_info(json.loads(raw_json, strict=False), scopes=scope)
    return gspread.authorize(creds)

# 1. حالة المندوبين (للمبات)
def get_status_map(delegates):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        try:
            ws = sheet.worksheet("Active_Users")
            data = ws.get_all_records()
            status = {}
            now = datetime.now()
            for row in data:
                u_name = row.get('المندوب') or list(row.values())[0]
                u_time = row.get('آخر_ظهور') or list(row.values())[1]
                try:
                    last_seen = datetime.strptime(str(u_time), "%Y-%m-%d %H:%M")
                    # يعتبر أونلاين إذا ظهر آخر 15 دقيقة
                    status[str(u_name).strip()] = (now - last_seen).total_seconds() < 900 
                except: continue
            return status
        except: return {}
    except: return {}

# 2. رسم اللمبات
def render_lights(delegates):
    status_map = get_status_map(delegates)
    html = '<div class="status-container">'
    for rep in delegates:
        is_on = status_map.get(rep.strip(), False)
        color = "on" if is_on else "off"
        initial = rep.strip()[0] if rep else "?"
        html += f'<div class="bulb {color}" title="{rep}">{initial}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# 3. جلب رقم الهاتف
def get_phone(name):
    try:
        client = get_gspread_client()
        sheet = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0")
        data = sheet.worksheet("البيانات").get_all_values()
        for row in data:
            if row[0].strip() == name.strip(): return str(row[1]).strip()
        return None
    except: return None

# 4. صناعة PDF
def make_pdf(name, items):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, f"Order: {name}", 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(15, 10, "#", 1, 0, 'C', 1)
    pdf.cell(135, 10, "Item", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Qty", 1, 1, 'C', 1)
    
    for i, item in enumerate(items, 1):
        clean_n = str(item['name']).encode('latin-1', 'ignore').decode('latin-1')
        pdf.cell(15, 10, str(i), 1, 0, 'C')
        pdf.cell(135, 10, clean_n[:45], 1, 0, 'L')
        pdf.cell(40, 10, str(item['qty']), 1, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# 5. تصديق الطلب
def finalize_order(name, items):
    try:
        client = get_gspread_client()
        ws = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0").worksheet(name.strip())
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        rows = [[now, i['name'], i['qty'], "تم التصديق", "جردة سيارة"] for i in items]
        for i in range(0, len(rows), 20):
            ws.append_rows(rows[i:i+20])
            time.sleep(0.5)
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# 6. جلب الأسماء (الفلتر الصارم)
def get_delegates():
    try:
        client = get_gspread_client()
        sheets = client.open_by_key("1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0").worksheets()
        
        # ⛔ القائمة السوداء (الكلمات الدقيقة)
        excluded = [
            "طلبات", "الذمم", "بيانات المندوبين", "عاجل", "الرئيسية", 
            "البيانات", "الاسعار", "الأسعار", "Sheet1", "Active_Users", "Item", "Products"
        ]
        
        # الفلترة: استبعاد أي اسم موجود بالقائمة السوداء (مع تنظيف المسافات)
        clean_list = []
        for s in sheets:
            title = s.title.strip()
            if title not in excluded:
                clean_list.append(title)
        return clean_list
    except: return []

# تحميل الداتا
@st.cache_data(ttl=60)
def load_data():
    try:
        url = f"https://docs.google.com/spreadsheets/d/1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0/gviz/tq?tqx=out:csv&sheet=طلبات"
        return pd.read_csv(url, header=None).dropna(how='all').iloc[:, :5].rename(columns={0:'cat', 1:'pack', 2:'sub', 3:'name', 4:'sci'})
    except: return None

df = load_data()

# إدارة الجلسة
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cust_name' not in st.session_state: st.session_state.cust_name = ""

# --- الصفحة الرئيسية ---
if df is not None:
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>لوحة تحكم حلباوي</h1></div>', unsafe_allow_html=True)
        
        # 1. اللمبات
        delegates_list = get_delegates()
        if delegates_list: render_lights(delegates_list)

        # 2. اختيار المندوب
        st.markdown("**👤 اختر المندوب:**")
        st.session_state.cust_name = st.selectbox("s_del", ["-- اختر --"] + delegates_list, label_visibility="collapsed")

        # 3. الأقسام
        st.write("---")
        for c in df['cat'].unique():
            if st.button(f"📦 {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        # 4. زر السلة (يظهر إذا في أغراض)
        if st.session_state.cart:
            st.markdown("---")
            if st.button("🛒 مراجعة الطلبية (السلة)", type="primary"):
                st.session_state.page = 'review'
                st.rerun()

    # --- صفحة التفاصيل ---
    elif st.session_state.page == 'details':
        if st.button("🏠 عودة"): st.session_state.page = 'home'; st.rerun()
        st.subheader(f"القسم: {st.session_state.sel_cat}")
        
        cat_df = df[df['cat'] == st.session_state.sel_cat]
        for _, row in cat_df.iterrows():
            key = f"q_{row['name']}"
            val = st.text_input(row['name'], key=key, value=st.session_state.cart.get(key, {}).get('qty', ""))
            if val: st.session_state.cart[key] = {'name': row['name'], 'qty': val}
            
        if st.button("✅ حفظ وإضافة للسلة"): st.session_state.page = 'home'; st.rerun()

    # --- صفحة المراجعة (الأزرار المطلوبة) ---
    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>إتمام الطلب</h1></div>', unsafe_allow_html=True)
        st.info(f"المندوب: {st.session_state.cust_name}")
        
        items = list(st.session_state.cart.values())
        for i, item in enumerate(items, 1):
            st.write(f"**{i}.** {item['name']} -> {item['qty']}")
            
        st.markdown("---")
        
        # 1. زر التصديق
        if st.button("🚀 تصديق الطلب (تحديث الجرد)"):
            if finalize_order(st.session_state.cust_name, items):
                st.success("✅ تم التحديث!")
        
        st.write("") # مسافة
        
        # 2. منطقة الأزرار (طباعة + واتساب)
        phone = get_phone(st.session_state.cust_name)
        if phone:
            # زر PDF (الأخضر)
            pdf_data = make_pdf(st.session_state.cust_name, items)
            st.download_button(
                label="🖨️ طباعة فاتورة (PDF)",
                data=pdf_data,
                file_name=f"Order_{st.session_state.cust_name}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # زر الواتساب (تحته)
            msg = f"مرحباً سيد {st.session_state.cust_name}، تم تصديق الطلبية."
            url = f"https://api.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{url}" target="_blank" class="wa-btn">📲 إرسال واتساب</a>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ لا يوجد رقم هاتف لهذا المندوب.")

    if st.button("🏠 الرئيسية"): st.session_state.page = 'home'; st.rerun()
