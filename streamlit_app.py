import streamlit as st
import urllib.parse
import requests
from datetime import datetime

# --- الإعدادات الأساسية ---
SCRIPT_URL = "ضع_رابط_الـ_WEB_APP_هنا"
RECEIVING_NUMBER = "9613220893"

st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# تصميم الواجهة
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .item-box { 
        display: inline-block; color: white !important; font-weight: bold !important; 
        font-size: 16px !important; background-color: #1E3A8A !important; 
        padding: 4px 10px; border-radius: 6px; text-align: right; min-width: 130px;
    }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; height: 35px !important; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 15px; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; }
    .review-box { background-color: #1c212d; border: 1px solid #fca311; padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# إدارة الحالة
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cart' not in st.session_state: st.session_state.cart = []

def ar_to_en_num(text):
    ar_nums = '٠١٢٣٤٥٦٧٨٩'
    en_nums = '0123456789'
    return text.translate(str.maketrans(ar_nums, en_nums))

def render_list_full(items_list, key_suffix):
    temp_list = []
    for item in items_list:
        if item.startswith("-"):
            st.markdown(f'<div style="color:#fca311; font-weight:bold; margin-top:10px; text-align:right;">{item[1:]}</div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<div class="item-box">{item}</div>', unsafe_allow_html=True)
            with c2:
                q = st.text_input("", key=f"{key_suffix}_{item}", label_visibility="collapsed", placeholder="0")
                if q:
                    q_en = ar_to_en_num(q)
                    if q_en.isdigit() and int(q_en) > 0:
                        temp_list.append({"item": item, "qty": q_en})
    return temp_list

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.image("https://raw.githubusercontent.com/helbawibros/-/main/Logo%20.JPG", use_container_width=True)
    st.markdown('<div class="header-box"><h1>قائمة الطلبيات</h1></div>', unsafe_allow_html=True)
    
    # قسم المراجعة
    if st.session_state.cart:
        st.markdown('<div class="review-box"><h3>📝 الأصناف المختارة:</h3>', unsafe_allow_html=True)
        for i, entry in enumerate(st.session_state.cart):
            st.write(f"{i+1}. {entry['item']} - الكمية: {entry['qty']}")
        
        col_send, col_clear = st.columns(2)
        with col_send:
            if st.button("🚀 إرسال الطلبية النهائية"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = "طلبية مبيعات جديدة:\n" + "-"*15 + "\n"
                for entry in st.session_state.cart:
                    # الإرسال للسيستم (Google Sheets)
                    payload = {"date": now, "item": entry['item'], "qty": entry['qty'], "status": "قيد الانتظار"}
                    try: requests.post(SCRIPT_URL, json=payload)
                    except: pass
                    msg += f"• {entry['item']}: {entry['qty']}\n"
                
                whatsapp_url = f"https://api.whatsapp.com/send?phone={RECEIVING_NUMBER}&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="background:#25d366;color:white;padding:15px;display:block;text-align:center;text-decoration:none;border-radius:10px;font-weight:bold;">تأكيد واتساب ✅</a>', unsafe_allow_html=True)
                st.session_state.cart = []
        with col_clear:
            if st.button("🗑️ مسح القائمة"):
                st.session_state.cart = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # كبسات الأقسام على نفس الخط
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("🌾 الحبوب"): st.session_state.page = 'grains'; st.rerun()
    with btn_col2:
        if st.button("🌶️ البهارات"): st.session_state.page = 'spices'; st.rerun()
    with btn_col3:
        if st.button("📋 صنف خاص"): st.session_state.page = 'special'; st.rerun()

# --- نموذج الحبوب ---
elif st.session_state.page == 'grains':
    st.markdown('<div class="header-box"><h2>🌾 نموذج الحبوب</h2></div>', unsafe_allow_html=True)
    
    with st.expander("📦 تعبئة 1000غ / 907غ", expanded=True):
        grain_items = [
            "-حمص", "حمص ١٢ (907غ)", "حمص ٩ (907غ)", "حمص كسر (907غ)", 
            "-فول", "فول حب (907غ)", "فول مجروش (1000غ)", "فول عريض (1000غ)", 
            "-فاصوليا", "فاصوليا صنوبرية (907غ)", "فاصوليا حمرا طويلة (1000غ)", "فاصوليا حمرا مدعبله (1000غ)", "فاصوليا عريضه (1000غ)", 
            "-عدس", "عدس ابيض رفيع (907غ)", "عدس احمر (907غ)", "عدس موردي/بلدي (907غ)", "عدس عريض (907غ)", 
            "-برغل", "برغل اسمر ناعم (907غ)", "برغل اسمر خشن (907غ)", "برغل اشقر ناعم (907غ)", "برغل اشقر خشن (907غ)",
            "-ارز", "ارز مصري (907غ)", "ارز إيطالي (907غ)", "ارز amirki (907غ)", "ارز بسمتي (907غ)", "ارز عنبري (1000غ)",
            "-سكر وطحين", "سكر حب (907غ)", "طحين فرخة (907غ)", "سميد (907غ)", "طحين زيرو (1000غ)"
        ]
        selections = render_list_full(grain_items, "gr")

    c_fix, c_back = st.columns(2)
    with c_fix:
        if st.button("✅ تثبيت الأصناف"):
            st.session_state.cart.extend(selections)
            st.session_state.page = 'home'; st.rerun()
    with c_back:
        if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- نموذج البهارات (نفس المنطق للأصناف الكاملة) ---
elif st.session_state.page == 'spices':
    st.markdown('<div class="header-box"><h2>🌶️ نموذج البهارات</h2></div>', unsafe_allow_html=True)
    with st.expander("🌶️ بهارات ناعمة 500 غ", expanded=True):
        spice_items = ["-بهارات", "بهار حلو", "فلفل أسود", "فلفل أحمر", "قرفة", "سبع بهارات", "كمون", "كزبرة", "كاري"]
        selections = render_list_full(spice_items, "sp")

    c_fix2, c_back2 = st.columns(2)
    with c_fix2:
        if st.button("✅ تثبيت الأصناف"):
            st.session_state.cart.extend(selections)
            st.session_state.page = 'home'; st.rerun()
    with c_back2:
        if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة الأصناف الخاصة ---
elif st.session_state.page == 'special':
    st.markdown('<div class="header-box"><h2>📋 صنف خاص وتفصيل</h2></div>', unsafe_allow_html=True)
    sp_item = st.text_input("اسم الصنف:")
    sp_qty = st.text_input("العدد / الكمية:")
    
    c_fix3, c_back3 = st.columns(2)
    with c_fix3:
        if st.button("✅ تثبيت الصنف الخاص"):
            if sp_item and sp_qty:
                st.session_state.cart.append({"item": f"خاص: {sp_item}", "qty": ar_to_en_num(sp_qty)})
                st.session_state.page = 'home'; st.rerun()
    with c_back3:
        if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()
