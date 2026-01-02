import streamlit as st
import urllib.parse
import requests
from datetime import datetime

# --- 1. الإعدادات الأساسية ورابط السيستم ---
SCRIPT_URL = "ضع_رابط_الـ_WEB_APP_هنا"
RECEIVING_NUMBER = "9613220893"

st.set_page_config(page_title="شركة حلباوي إخوان", layout="wide")

# --- 2. تصميم الواجهة ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .category-header { 
        background-color: #e9ecef; color: #1E3A8A; padding: 8px 12px; border-radius: 5px; 
        font-weight: bold; font-size: 16px; margin-top: 15px; border-right: 5px solid #fca311; text-align: right;
    }
    .item-box { 
        display: inline-block; color: white !important; font-weight: bold !important; 
        font-size: 16px !important; background-color: #1E3A8A !important; 
        padding: 5px 12px; border-radius: 8px; text-align: right; min-width: 140px;
    }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; height: 40px !important; font-size: 20px !important; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 50px; width: 100%; }
    .review-box { background-color: #1c212d; border: 1px solid #fca311; padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. إدارة الحالة ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cart' not in st.session_state: st.session_state.cart = []

def ar_to_en_num(text):
    ar_nums = '٠١٢٣٤٥٦٧٨٩'
    en_nums = '0123456789'
    return text.translate(str.maketrans(ar_nums, en_nums))

# --- 4. دوال العرض الذكية ---
def render_standard(items, key, weight=""):
    sels = []
    for item in items:
        if item.startswith("-"):
            st.markdown(f'<div class="category-header">{item[1:]}</div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns([2.5, 1])
            with c1: st.markdown(f'<div class="item-box">{item}</div>', unsafe_allow_html=True)
            with c2:
                q = st.text_input("", key=f"{key}_{item}", label_visibility="collapsed", placeholder="0")
                if q:
                    q_en = ar_to_en_num(q)
                    if q_en.isdigit() and int(q_en) > 0:
                        # استثناء ذرة بوشار 500غ
                        if "ذره بوشار" in item and weight == "500غ":
                            name = item 
                        else:
                            name = f"{item} {weight}" if weight else item
                        sels.append({"item": name.strip(), "qty": q_en})
    return sels

def render_200g_special(items, key):
    sels = []
    cat = ""
    for item in items:
        if item.startswith("-"):
            cat = item[1:]
            st.markdown(f'<div class="category-header">{cat}</div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns([2.5, 1])
            with c1: st.markdown(f'<div class="item-box">{item}</div>', unsafe_allow_html=True)
            with c2:
                q = st.text_input("", key=f"{key}_{item}", label_visibility="collapsed", placeholder="0")
                if q:
                    q_en = ar_to_en_num(q)
                    if q_en.isdigit() and int(q_en) > 0:
                        name = f"{item} 200غ" if cat == "مختلف" else f"{cat} {item} 200غ"
                        sels.append({"item": name, "qty": q_en})
    return sels

# --- 5. التنقل بين الصفحات ---

# الصفحة الرئيسية
if st.session_state.page == 'home':
    st.image("https://raw.githubusercontent.com/helbawibros/-/main/Logo%20.JPG", use_container_width=True)
    st.markdown('<div class="header-box"><h1>نظام طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    
    if st.session_state.cart:
        st.markdown('<div class="review-box"><h3>📝 المراجعة قبل الإرسال:</h3>', unsafe_allow_html=True)
        for entry in st.session_state.cart:
            st.write(f"• {entry['item']} : {entry['qty']}")
        
        c_send, c_clear = st.columns(2)
        with c_send:
            if st.button("🚀 إرسال الطلبية"):
                msg = "طلبية مبيعات جديدة:\n" + "-"*15 + "\n"
                for entry in st.session_state.cart:
                    msg += f"• {entry['item']} : {entry['qty']}\n"
                url = f"https://api.whatsapp.com/send?phone={RECEIVING_NUMBER}&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank" style="background:#25d366;color:white;padding:15px;display:block;text-align:center;text-decoration:none;border-radius:10px;font-weight:bold;">تأكيد واتساب ✅</a>', unsafe_allow_html=True)
                st.session_state.cart = []
        with c_clear:
            if st.button("🗑️ مسح الكل"):
                st.session_state.cart = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🌾 الحبوب"): st.session_state.page = 'grains'; st.rerun()
    with c2:
        if st.button("🌶️ البهارات"): st.session_state.page = 'spices'; st.rerun()
    with c3:
        if st.button("📋 صنف خاص"): st.session_state.page = 'special'; st.rerun()

# صفحة الحبوب
elif st.session_state.page == 'grains':
    st.markdown('<div class="header-box"><h2>🌾 نموذج الحبوب</h2></div>', unsafe_allow_html=True)
    g_sels = []
    
    with st.expander("📦 تعبئة 1000غ / 907غ", expanded=True):
        g_sels += render_standard(["-حمص", "حمص ١٢ (907غ)", "حمص ٩ (907غ)", "حمص كسر (907غ)", "-فول", "فول حب (907غ)", "فول مجروش (1000غ)", "فول عريض (1000غ)", "-عدس", "عدس ابيض رفيع (907غ)", "عدس احمر (907غ)", "-أرز", "أرز مصري (907غ)", "أرز إيطالي (907غ)", "أرز أمريكي (907غ)", "أرز بسمتي (907غ)", "أرز عنبري (1000غ)"], "g1k")

    with st.expander("📦 تعبئة 500غ / 454غ"):
        g_sels += render_standard(["-سمسم", "سمسم مقشور", "سمسم محمص", "-ذره", "ذره بوشار (454غ)", "ذره مجروشه (500غ)", "-سكر", "سكر ناعم", "سكر نبات"], "g500", "500غ")

    with st.expander("📦 تعبئة 200غ"):
        g_sels += render_200g_special(["-سمسم", "مقشور", "محمص", "-نشاء", "حب", "ناعم", "-فرمسيل", "شوكولا", "ملون", "-ملوخية", "نايلون", "كرتون", "-زعتر", "محوج", "حلبي", "-مختلف", "برش جوز الهند", "بامية زهرة", "فلافل علب"], "g200")
    
    with st.expander("📋 تعبئة مختلفة"):
        g_sels += render_standard(["-ملح", "ناعم 700 غ × 24", "ناعم 3 كلغ × 6", "-قمح", "مقشور 2 كلغ", "مقشور 5 كلغ"], "gmisc")

    if st.button("✅ تثبيت الحبوب"):
        st.session_state.cart.extend(g_sels); st.session_state.page = 'home'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# صفحة البهارات
elif st.session_state.page == 'spices':
    st.markdown('<div class="header-box"><h2>🌶️ نموذج البهارات</h2></div>', unsafe_allow_html=True)
    s_sels = render_standard(["-ناعمة 500غ", "بهار حلو", "فلفل أسود", "سبع بهارات", "-ناعمة 50غ", "كمون", "قرفة"], "sp")
    if st.button("✅ تثبيت البهارات"):
        st.session_state.cart.extend(s_sels); st.session_state.page = 'home'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# صفحة خاص
elif st.session_state.page == 'special':
    st.markdown('<div class="header-box"><h2>📋 طلب خاص</h2></div>', unsafe_allow_html=True)
    sp_i = st.text_input("الصنف:")
    sp_q = st.text_input("الكمية:")
    if st.button("✅ تثبيت"):
        if sp_i and sp_q:
            st.session_state.cart.append({"item": f"خاص: {sp_i}", "qty": ar_to_en_num(sp_q)})
            st.session_state.page = 'home'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()
