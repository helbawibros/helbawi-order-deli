import streamlit as st
import urllib.parse
import requests
from datetime import datetime

# --- إعدادات الربط والواتساب ---
SCRIPT_URL = "ضع_رابط_الـ_WEB_APP_هنا"
RECEIVING_NUMBER = "9613220893"

st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# تصميم الواجهة
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .category-header { 
        background-color: #e9ecef; color: #1E3A8A; padding: 6px 10px; border-radius: 5px; 
        font-weight: bold; font-size: 15px; margin-top: 12px; border-right: 5px solid #fca311; text-align: right;
    }
    .item-box { 
        display: inline-block; color: white !important; font-weight: bold !important; 
        font-size: 16px !important; background-color: #1E3A8A !important; 
        padding: 4px 10px; border-radius: 6px; text-align: right; min-width: 130px;
    }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; height: 35px !important; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 10px; border-radius: 10px; margin-bottom: 15px; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; width: 100%; }
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

def render_list_system(items_list, key_suffix):
    temp_selections = []
    for item in items_list:
        if item.startswith("-"):
            st.markdown(f'<div class="category-header">{item[1:]}</div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns([2.5, 1])
            with c1: st.markdown(f'<div class="item-box">{item}</div>', unsafe_allow_html=True)
            with c2:
                q = st.text_input("", key=f"{key_suffix}_{item}", label_visibility="collapsed", placeholder="0")
                if q:
                    q_en = ar_to_en_num(q)
                    if q_en.isdigit() and int(q_en) > 0:
                        temp_selections.append({"item": item, "qty": q_en})
    return temp_selections

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.image("https://raw.githubusercontent.com/helbawibros/-/main/Logo%20.JPG", use_container_width=True)
    st.markdown('<div class="header-box"><h1>قائمة الطلبيات</h1></div>', unsafe_allow_html=True)
    
    if st.session_state.cart:
        st.markdown('<div class="review-box"><h3>📝 مراجعة الطلب:</h3>', unsafe_allow_html=True)
        for i, entry in enumerate(st.session_state.cart):
            st.write(f"{i+1}. {entry['item']} ← {entry['qty']}")
        
        col_send, col_clear = st.columns(2)
        with col_send:
            if st.button("🚀 إرسال الطلبية النهائية"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = "طلبية مبيعات جديدة:\n" + "-"*15 + "\n"
                for entry in st.session_state.cart:
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

    # الكبسات الثلاث بجانب بعضها
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🌾 الحبوب"): st.session_state.page = 'grains'; st.rerun()
    with c2:
        if st.button("🌶️ البهارات"): st.session_state.page = 'spices'; st.rerun()
    with c3:
        if st.button("📋 خاص"): st.session_state.page = 'special'; st.rerun()

# --- نموذج الحبوب (كامل) ---
elif st.session_state.page == 'grains':
    st.markdown('<div class="header-box"><h2>🌾 نموذج الحبوب</h2></div>', unsafe_allow_html=True)
    full_g_order = []
    
    with st.expander("📦 تعبئة 1000غ / 907غ"):
        full_g_order += render_list_system(["-حمص", "حمص ١٢ (907غ)", "حمص ٩ (907غ)", "حمص كسر (907غ)", "-فول", "فول حب (907غ)", "فول مجروش (1000غ)", "فول عريض (1000غ)", "-فاصوليا", "فاصوليا صنوبرية (907غ)", "فاصوليا حمرا طويلة (1000غ)", "فاصوليا حمرا مدعبله (1000غ)", "فاصوليا عريضه (1000غ)", "-عدس", "عدس ابيض رفيع (907غ)", "عدس احمر (907غ)", "عدس موردي/بلدي (907غ)", "عدس عريض (907غ)", "-برغل", "برغل اسمر ناعم (907غ)", "برغل اسمر خشن (907غ)", "برغل اشقر ناعم (907غ)", "برغل اشقر خشن (907غ)", "-ارز", "ارز مصري (907غ)", "ارز إيطالي (907غ)", "ارز amirki (907غ)", "ارز بسمتي (907غ)", "-سكر", "سكر حب (907غ)", "-طحين", "طحين فرخة (907غ)", "طحين زيرو (1000غ)"], "g1k")

    with st.expander("📦 تعبئة 500غ / 454غ"):
        full_g_order += render_list_system(["-سمسم", "سمسم مقشور", "سمسم محمص", "-نشاء", "نشاء ناعم", "نشاء حب", "-زعتر", "زعتر محوج", "-سكر", "سكر ناعم", "سكر نبات", "-شوفان", "شوفان مبروش", "شوفان حب"], "g500")

    with st.expander("📦 تعبئة 200غ"):
        full_g_order += render_list_system(["-سمسم", "مقشور", "محمص", "-نشاء", "حب", "ناعم", "-ملوخية", "نايلون", "كرتون"], "g200")

    with st.expander("📋 تعبئة مختلفة"):
        full_g_order += render_list_system(["-ملح", "ناعم 700 غ × 24", "ناعم 3 كلغ × 6", "-قمح", "مقشور 2 كلغ", "مقشور 5 كلغ"], "gmisc")

    col_fix, col_back = st.columns(2)
    with col_fix:
        if st.button("✅ تثبيت الحبوب"):
            st.session_state.cart.extend(full_g_order)
            st.session_state.page = 'home'; st.rerun()
    with col_back:
        if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- نموذج البهارات (كامل) ---
elif st.session_state.page == 'spices':
    st.markdown('<div class="header-box"><h2>🌶️ نموذج البهارات</h2></div>', unsafe_allow_html=True)
    full_s_order = []

    with st.expander("🌶️ بهارات ناعمة 500 غ"):
        full_s_order += render_list_system(["-أساسية", "بهار حلو", "فلفل أسود", "فلفل أحمر", "قرفة", "سبع بهارات", "كمون", "كزبرة", "كراوية", "كاري", "يانسون", "-خاصة", "كبة", "مغربية", "فلافل", "كبسة", "دجاج", "طاووق"], "s500n")

    with st.expander("🌿 بهارات حب 500 غ"):
        full_s_order += render_list_system(["-حب", "بهار حلو", "فلفل أسود", "قرفة", "كمون", "يانسون", "قرنفل", "هال", "ورق غار"], "s500h")

    with st.expander("🌶️ بهارات 50 غ / 20 غ"):
        full_s_order += render_list_system(["-ناعمة 50غ", "بهار حلو", "فلفل أسود", "-حب 20غ", "جوزة الطيب", "محلب", "قرنفل", "هال"], "s50_20")

    with st.expander("📋 أصناف متنوعة"):
        full_s_order += render_list_system(["-حامض", "حامض (500 غ)", "حامض (1000 غ)", "-سماق", "سماق (500 غ)", "سماق (1000 غ)"], "smisc")

    col_fix2, col_back2 = st.columns(2)
    with col_fix2:
        if st.button("✅ تثبيت البهارات"):
            st.session_state.cart.extend(full_s_order)
            st.session_state.page = 'home'; st.rerun()
    with col_back2:
        if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- صنف خاص (مطور) ---
elif st.session_state.page == 'special':
    st.markdown('<div class="header-box"><h2>📋 صنف خاص وتفصيل</h2></div>', unsafe_allow_html=True)
    sp_item = st.text_input("اسم الصنف (مثلاً: حمص حب):")
    sp_pack = st.text_input("التعبئة (مثلاً: كيس ٥ كيلو):")
    sp_qty = st.text_input("العدد المطلوبة:")
    
    c_fix3, c_back3 = st.columns(2)
    with c_fix3:
        if st.button("✅ تثبيت الصنف الخاص"):
            if sp_item and sp_qty:
                st.session_state.cart.append({"item": f"خاص: {sp_item} ({sp_pack})", "qty": ar_to_en_num(sp_qty)})
                st.session_state.page = 'home'; st.rerun()
    with c_back3:
        if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()
