import streamlit as st
import urllib.parse
import requests
from datetime import datetime

# --- إعدادات أساسية ---
SCRIPT_URL = "ضع_رابط_الـ_WEB_APP_هنا"
RECEIVING_NUMBER = "9613220893"

st.set_page_config(page_title="شركة حلباوي إخوان", layout="wide")

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

if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cart' not in st.session_state: st.session_state.cart = []

def ar_to_en_num(text):
    ar_nums = '٠١٢٣٤٥٦٧٨٩'
    en_nums = '0123456789'
    return text.translate(str.maketrans(ar_nums, en_nums))

# الدالة المعدلة لإضافة وزن القسم لاسم الصنف
def render_list_with_weight(items_list, key_suffix, weight_label):
    selections = []
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
                        # هنا ندمج اسم الصنف مع وزن القسم
                        full_name = f"{item} ({weight_label})" if weight_label else item
                        selections.append({"item": full_name, "qty": q_en})
    return selections

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.image("https://raw.githubusercontent.com/helbawibros/-/main/Logo%20.JPG", use_container_width=True)
    st.markdown('<div class="header-box"><h1>نظام طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    
    if st.session_state.cart:
        st.markdown('<div class="review-box"><h3>📝 المراجعة قبل الإرسال:</h3>', unsafe_allow_html=True)
        for i, entry in enumerate(st.session_state.cart):
            # التنسيق المطلوب: الصنف : العدد
            st.write(f"{i+1}. {entry['item']} : {entry['qty']}")
        
        c_send, c_clear = st.columns(2)
        with c_send:
            if st.button("🚀 إرسال الطلبية النهائية"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = "طلبية مبيعات جديدة:\n" + "-"*15 + "\n"
                for entry in st.session_state.cart:
                    payload = {"date": now, "item": entry['item'], "qty": entry['qty'], "status": "قيد الانتظار"}
                    try: requests.post(SCRIPT_URL, json=payload)
                    except: pass
                    msg += f"• {entry['item']} : {entry['qty']}\n"
                
                whatsapp_url = f"https://api.whatsapp.com/send?phone={RECEIVING_NUMBER}&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="background:#25d366;color:white;padding:15px;display:block;text-align:center;text-decoration:none;border-radius:10px;font-weight:bold;">تأكيد واتساب ✅</a>', unsafe_allow_html=True)
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

# --- صفحة الحبوب ---
elif st.session_state.page == 'grains':
    st.markdown('<div class="header-box"><h2>🌾 نموذج الحبوب</h2></div>', unsafe_allow_html=True)
    grains_sel = []
    
    with st.expander("📦 تعبئة 1000غ / 907غ"):
        # ملاحظة: بعض أصناف الحبوب عندها الوزن مكتوب أصلاً، فمنحط الوزن فاضي هون
        grains_sel += render_list_with_weight(["-حمص", "حمص ١٢ (907غ)", "حمص ٩ (907غ)", "حمص كسر (907غ)", "-فول", "فول حب (907غ)", "فول مجروش (1000غ)", "فول عريض (1000غ)", "-فاصوليا", "فاصوليا صنوبرية (907غ)", "-عدس", "عدس ابيض رفيع (907غ)", "عدس احمر (907غ)"], "g1", "")

    with st.expander("📦 تعبئة 500غ / 454غ"):
        grains_sel += render_list_with_weight(["-سمسم", "سمسم مقشور", "سمسم محمص", "-نشاء", "نشاء ناعم", "-سكر", "سكر ناعم"], "g5", "500غ")

    c_fix, c_back = st.columns(2)
    with c_fix:
        if st.button("✅ تثبيت الحبوب"):
            st.session_state.cart.extend(grains_sel)
            st.session_state.page = 'home'; st.rerun()
    with c_back:
        if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة البهارات ---
elif st.session_state.page == 'spices':
    st.markdown('<div class="header-box"><h2>🌶️ نموذج البهارات</h2></div>', unsafe_allow_html=True)
    spices_sel = []

    with st.expander("🌶️ بهارات ناعمة 500 غ"):
        spices_sel += render_list_with_weight(["بهار حلو", "فلفل أسود", "فلفل أحمر", "قرفة", "سبع بهارات"], "s5n", "500غ ناعم")

    with st.expander("🌶️ بهارات 50 غ"):
        spices_sel += render_list_with_weight(["بهار حلو", "فلفل أسود", "فلفل أحمر", "قرفة", "سبع بهارات"], "s50", "50غ")

    c_fix2, c_back2 = st.columns(2)
    with c_fix2:
        if st.button("✅ تثبيت البهارات"):
            st.session_state.cart.extend(spices_sel)
            st.session_state.page = 'home'; st.rerun()
    with c_back2:
        if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة صنف خاص ---
elif st.session_state.page == 'special':
    st.markdown('<div class="header-box"><h2>📋 طلب صنف خاص</h2></div>', unsafe_allow_html=True)
    sp_i = st.text_input("اسم الصنف:")
    sp_p = st.text_input("التعبئة:")
    sp_q = st.text_input("العدد:")
    
    if st.button("✅ تثبيت"):
        if sp_i and sp_q:
            full_item = f"{sp_i} ({sp_p})" if sp_p else sp_i
            st.session_state.cart.append({"item": full_item, "qty": ar_to_en_num(sp_q)})
            st.session_state.page = 'home'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()
