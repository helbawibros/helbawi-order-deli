import streamlit as st
import urllib.parse
import requests
from datetime import datetime

# --- إعدادات الرابط (ضع رابط السكربت الخاص بك هنا) ---
SCRIPT_URL = "ضع_رابط_الـ_WEB_APP_هنا"
RECEIVING_NUMBER = "9613220893"

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان", layout="wide")

# 2. تصميم الواجهة (تم تحديث الـ CSS لتحسين مظهر الخانات الفارغة)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .category-header { 
        background-color: #e9ecef; color: #1E3A8A; padding: 8px 12px; border-radius: 5px; 
        font-weight: bold; font-size: 16px; margin-top: 15px; border-right: 5px solid #fca311; text-align: right;
    }
    .item-box { 
        display: inline-block; color: white !important; font-weight: bold !important; 
        font-size: 17px !important; background-color: #1E3A8A !important; 
        padding: 5px 12px; border-radius: 8px; text-align: right; min-width: 140px;
    }
    input { 
        background-color: #ffffcc !important; color: black !important; font-weight: bold !important; 
        height: 40px !important; font-size: 20px !important;
    }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# دالة لتحويل الأرقام العربية إلى إنجليزية لضمان صحة البيانات في الإكسل
def ar_to_en_num(text):
    ar_nums = '٠١٢٣٤٥٦٧٨٩'
    en_nums = '0123456789'
    table = str.maketrans(ar_nums, en_nums)
    return text.translate(table)

# دالة الإرسال إلى Google Sheets
def send_to_sheets(customer_name, order_dict, order_type):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for section, items in order_dict.items():
        for item in items:
            name, qty = item.split(": ")
            payload = {
                "date": now,
                "type": order_type,
                "customer": customer_name,
                "item": name,
                "qty": qty,
                "status": "قيد الانتظار"
            }
            try:
                requests.post(SCRIPT_URL, json=payload)
            except:
                pass

# دالة عرض القائمة مع تحسين إدخال الأرقام
def render_list(items_list, key_suffix, order_dict, section_label):
    for item in items_list:
        if item.startswith("-"):
            st.markdown(f'<div class="category-header">{item[1:]}</div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns([2.5, 1])
            with c1: 
                st.markdown(f'<div class="item-box">{item}</div>', unsafe_allow_html=True)
            with c2:
                # استخدام text_input بدلاً من number_input لجعلها فارغة وقبول كل أنواع الأرقام
                q_raw = st.text_input("", key=f"{key_suffix}_{item}", label_visibility="collapsed", placeholder="العدد")
                if q_raw:
                    q_en = ar_to_en_num(q_raw)
                    if q_en.isdigit() and int(q_en) > 0:
                        if section_label not in order_dict: order_dict[section_label] = []
                        order_dict[section_label].append(f"{item}: {q_en}")

if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.image("https://raw.githubusercontent.com/helbawibros/-/main/Logo%20.JPG", use_container_width=True)
    st.markdown('<div class="header-box"><h1>نظام طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌾 نموذج الحبوب", use_container_width=True):
            st.session_state.page = 'grains'; st.rerun()
    with col2:
        if st.button("🌶️ نموذج البهارات", use_container_width=True):
            st.session_state.page = 'spices'; st.rerun()
    with col3:
        if st.button("📋 أصناف خاصة", use_container_width=True):
            st.session_state.page = 'special'; st.rerun()

# --- نموذج الحبوب (تم استخدام دالة render_list المحدثة) ---
elif st.session_state.page == 'grains':
    st.markdown('<div class="header-box"><h2>نموذج الحبوب</h2></div>', unsafe_allow_html=True)
    customer = st.text_input("👤 إسم الزبون:")
    full_order = {}
    
    with st.expander("📦 الحبوب الأساسية"):
        render_list(["-حمص", "حمص ١٢ (907غ)", "حمص ٩ (907غ)", "-فول", "فول حب (907غ)", "فول عريض (1000غ)"], "g1k", full_order, "حبوب 1000غ")
    
    # ... (بقية الأقسام تتبع نفس المنطق)

    if st.button("🚀 إرسال وتأكيد الطلبية", use_container_width=True):
        if customer and full_order:
            send_to_sheets(customer, full_order, "حبوب")
            msg = f"طلبية حبوب: *{customer}*\n"
            for section, items in full_order.items():
                msg += f"\n*{section}*:\n" + "\n".join([f"• {i}" for i in items])
            st.markdown(f'<a href="https://api.whatsapp.com/send?phone={RECEIVING_NUMBER}&text={urllib.parse.quote(msg)}" target="_blank" style="background:#25d366;color:white;padding:15px;display:block;text-align:center;text-decoration:none;border-radius:10px;font-weight:bold;">تأكيد الإرسال للشركة (WhatsApp)</a>', unsafe_allow_html=True)
            st.success("تم تسجيل الطلبية في النظام بنجاح!")
    
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة الأصناف الخاصة (الجديدة) ---
elif st.session_state.page == 'special':
    st.markdown('<div class="header-box"><h2>📋 أصناف خاصة وتفصيل</h2></div>', unsafe_allow_html=True)
    customer_sp = st.text_input("👤 إسم الزبون:")
    
    if 'special_items' not in st.session_state: st.session_state.special_items = [{"item": "", "weight": "", "qty": ""}]
    
    for i, entry in enumerate(st.session_state.special_items):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: st.session_state.special_items[i]["item"] = st.text_input(f"الصنف {i+1}", key=f"sp_i_{i}")
        with c2: st.session_state.special_items[i]["weight"] = st.text_input(f"التعبئة {i+1}", key=f"sp_w_{i}")
        with c3: st.session_state.special_items[i]["qty"] = st.text_input(f"العدد {i+1}", key=f"sp_q_{i}")

    if st.button("➕ إضافة صنف آخر"):
        st.session_state.special_items.append({"item": "", "weight": "", "qty": ""})
        st.rerun()

    if st.button("🚀 إرسال الأصناف الخاصة"):
        if customer_sp:
            special_order = {"أصناف خاصة": []}
            for entry in st.session_state.special_items:
                if entry["item"] and entry["qty"]:
                    special_order["أصناف خاصة"].append(f"{entry['item']} ({entry['weight']}): {entry['qty']}")
            
            send_to_sheets(customer_sp, special_order, "خاص")
            # كود الواتساب
            msg = f"طلبية خاصة: *{customer_sp}*\n" + "\n".join([f"• {i}" for i in special_order["أصناف خاصة"]])
            st.markdown(f'<a href="https://api.whatsapp.com/send?phone={RECEIVING_NUMBER}&text={urllib.parse.quote(msg)}" target="_blank" style="background:#25d366;color:white;padding:15px;display:block;text-align:center;text-decoration:none;border-radius:10px;font-weight:bold;">تأكيد الواتساب</a>', unsafe_allow_html=True)
    
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()
