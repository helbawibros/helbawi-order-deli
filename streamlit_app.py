import streamlit as st
import urllib.parse
import requests
from datetime import datetime

# --- إعدادات الرابط (ضع رابط السكربت الخاص بك هنا) ---
SCRIPT_URL = "ضع_رابط_الـ_WEB_APP_هنا"
RECEIVING_NUMBER = "9613220893"

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام طلبيات حلباوي", layout="wide")

# 2. تصميم الواجهة
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .item-box { 
        display: inline-block; color: white !important; font-weight: bold !important; 
        font-size: 17px !important; background-color: #1E3A8A !important; 
        padding: 5px 12px; border-radius: 8px; text-align: right; min-width: 140px;
    }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 45px; width: 100%; }
    .review-box { background-color: #1c212d; border: 1px solid #fca311; padding: 15px; border-radius: 10px; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة الحالة (Session State)
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cart' not in st.session_state: st.session_state.cart = [] # سلة التسوق

def ar_to_en_num(text):
    ar_nums = '٠١٢٣٤٥٦٧٨٩'
    en_nums = '0123456789'
    return text.translate(str.maketrans(ar_nums, en_nums))

# دالة عرض الأصناف مع زر تثبيت
def render_section(items_list, section_label):
    temp_selections = []
    for item in items_list:
        if item.startswith("-"):
            st.markdown(f'<div style="color:#fca311; font-weight:bold; margin-top:10px;">{item[1:]}</div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<div class="item-box">{item}</div>', unsafe_allow_html=True)
            with c2:
                q = st.text_input("", key=f"q_{section_label}_{item}", label_visibility="collapsed", placeholder="0")
                if q:
                    q_en = ar_to_en_num(q)
                    if q_en.isdigit() and int(q_en) > 0:
                        temp_selections.append({"item": item, "qty": q_en, "section": section_label})
    return temp_selections

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.image("https://raw.githubusercontent.com/helbawibros/-/main/Logo%20.JPG", use_container_width=True)
    st.markdown('<div class="header-box"><h1>قائمة الطلبيات</h1></div>', unsafe_allow_html=True)
    
    # عرض المراجعة إذا كان هناك أصناف مثبته
    if st.session_state.cart:
        st.markdown('<div class="review-box"><h3>📝 مراجعة الطلب الحالي:</h3>', unsafe_allow_html=True)
        for i, entry in enumerate(st.session_state.cart):
            st.write(f"{i+1}. {entry['item']} - الكمية: {entry['qty']} ({entry['section']})")
        
        col_send, col_clear = st.columns(2)
        with col_send:
            if st.button("🚀 إرسال الطلب النهائي (واتساب + سيستم)"):
                # هنا كود الإرسال المزدوج
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = "طلبية مبيعات جديدة:\n"
                for entry in st.session_state.cart:
                    # إرسال للسيستم
                    payload = {"date": now, "item": entry['item'], "qty": entry['qty'], "status": "قيد الانتظار"}
                    requests.post(SCRIPT_URL, json=payload)
                    msg += f"• {entry['item']}: {entry['qty']}\n"
                
                # إرسال واتساب
                st.markdown(f'<a href="https://api.whatsapp.com/send?phone={RECEIVING_NUMBER}&text={urllib.parse.quote(msg)}" target="_blank" style="background:#25d366;color:white;padding:15px;display:block;text-align:center;text-decoration:none;border-radius:10px;font-weight:bold;">تأكيد عبر واتساب</a>', unsafe_allow_html=True)
                st.session_state.cart = [] # تفريغ السلة بعد الإرسال
        with col_clear:
            if st.button("🗑️ مسح الكل"):
                st.session_state.cart = []
                st.rerun()
        st.markdown('</div><br>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🌾 الحبوب"): st.session_state.page = 'grains'; st.rerun()
    with c2:
        if st.button("🌶️ البهارات"): st.session_state.page = 'spices'; st.rerun()
    with c3:
        if st.button("📋 خاص"): st.session_state.page = 'special'; st.rerun()

# --- نموذج الحبوب ---
elif st.session_state.page == 'grains':
    st.markdown('<div class="header-box"><h2>🌾 أصناف الحبوب</h2></div>', unsafe_allow_html=True)
    
    with st.expander("📦 تعبئة 1000غ"):
        selections = render_section(["-حمص", "حمص فجلي", "حمص كسر", "-عدس", "عدس أحمر", "عدس عريض"], "حبوب")

    col_fix, col_back = st.columns(2)
    with col_fix:
        if st.button("✅ تثبيت هذه الأصناف"):
            st.session_state.cart.extend(selections)
            st.success("تم التثبيت بنجاح!")
            st.session_state.page = 'home'; st.rerun()
    with col_back:
        if st.button("🔙 عودة بدون تثبيت"): st.session_state.page = 'home'; st.rerun()

# --- صفحة الأصناف الخاصة ---
elif st.session_state.page == 'special':
    st.markdown('<div class="header-box"><h2>📋 طلب خاص</h2></div>', unsafe_allow_html=True)
    s_item = st.text_input("الصنف:")
    s_qty = st.text_input("الكمية:")
    
    col_fix2, col_back2 = st.columns(2)
    with col_fix2:
        if st.button("✅ تثبيت الطلب الخاص"):
            if s_item and s_qty:
                st.session_state.cart.append({"item": s_item, "qty": ar_to_en_num(s_qty), "section": "خاص"})
                st.session_state.page = 'home'; st.rerun()
    with col_back2:
        if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()
