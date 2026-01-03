import streamlit as st
import urllib.parse

# --- الإعدادات الأساسية ---
RECEIVING_NUMBER = "9613220893"

st.set_page_config(page_title="شركة حلباوي إخوان", layout="wide")

# --- التصميم CSS ---
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
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; height: 40px !important; font-size: 20px !important; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 50px; width: 100%; }
    .review-box { background-color: #1c212d; border: 1px solid #fca311; padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة الحالة (Session State) ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cart' not in st.session_state: st.session_state.cart = []

def ar_to_en_num(text):
    ar_nums = '٠١٢٣٤٥٦٧٨٩'
    en_nums = '0123456789'
    return text.translate(str.maketrans(ar_nums, en_nums))

def render_billing_items(items_dict, key):
    sels = []
    for display_name, billing_name in items_dict.items():
        if display_name.startswith("-"):
            st.markdown(f'<div class="category-header">{display_name[1:]}</div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns([2.5, 1])
            with c1: st.markdown(f'<div class="item-box">{display_name}</div>', unsafe_allow_html=True)
            with c2:
                q = st.text_input("", key=f"{key}_{display_name}", label_visibility="collapsed", placeholder="0")
                if q:
                    q_en = ar_to_en_num(q)
                    if q_en.isdigit() and int(q_en) > 0:
                        sels.append({"item": billing_name, "qty": q_en})
    return sels

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.image("https://raw.githubusercontent.com/helbawibros/-/main/Logo%20.JPG", use_container_width=True)
    st.markdown('<div class="header-box"><h1>نظام طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    
    if st.session_state.cart:
        st.markdown('<div class="review-box"><h3>📝 المراجعة:</h3>', unsafe_allow_html=True)
        for entry in st.session_state.cart:
            st.write(f"• {entry['item']} : {entry['qty']}")
        c_send, c_clear = st.columns(2)
        with c_send:
            if st.button("🚀 إرسال"):
                msg = "طلبية مبيعات جديدة:\n" + "-"*15 + "\n"
                for entry in st.session_state.cart: msg += f"• {entry['item']} : {entry['qty']}\n"
                url = f"https://api.whatsapp.com/send?phone={RECEIVING_NUMBER}&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank" style="background:#25d366;color:white;padding:15px;display:block;text-align:center;text-decoration:none;border-radius:10px;font-weight:bold;">تأكيد واتساب ✅</a>', unsafe_allow_html=True)
                st.session_state.cart = []
        with c_clear:
            if st.button("🗑️ مسح الكل"): st.session_state.cart = []; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    c1, col_sp, c3 = st.columns(3)
    with c1:
        if st.button("🌾 الحبوب"): st.session_state.page = 'grains'; st.rerun()
    with col_sp:
        if st.button("🌶️ البهارات"): st.session_state.page = 'spices'; st.rerun()
    with c3:
        if st.button("📋 صنف خاص"): st.session_state.page = 'special'; st.rerun()

# --- صفحة الحبوب ---
elif st.session_state.page == 'grains':
    st.markdown('<div class="header-box"><h2>🌾 نموذج الحبوب (1000غ/907غ)</h2></div>', unsafe_allow_html=True)
    
    items_1k = {
        "- الحمص والفول": "",
        "حمص فحلي 12": "حمص فحلي \"12\" 907غ",
        "حمص فحلي 9": "حمص فحلي \"9\" 907غ",
        "حمص كسر": "حمص كسر 1000غ",
        "فول حب": "فول حب 1000غ",
        "فول مجروش": "فول مجروش 1000غ",
        "فول عريض": "فول عريض 1000غ",
        "- الفاصوليا": "",
        "فاصوليا صنوبرية": "فاصوليا صنوبرية 907غ",
        "فاصوليا حمرا طويلة": "فاصوليا حمرا طويلة 1000غ",
        "فاصوليا حمرا مدعبلة": "فاصوليا حمرا مدعبلة 1000غ",
        "فاصوليا عريضة": "فاصوليا عريضة 1000غ",
        "- العدس": "",
        "عدس أبيض بلدي": "عدس أبيض بلدي 907غ",
        "عدس أحمر": "عدس أحمر 907غ",
        "عدس أحمر موردي": "عدس أحمر موردي 1000غ",
        "عدس عريض": "عدس عريض 907غ",
        "عدس مجروش": "عدس مجروش 907غ",
        "- البرغل": "",
        "برغل أسمر ناعم": "برغل أسمر ناعم 907غ",
        "برغل أسمر خشن": "برغل أسمر خشن 907غ",
        "برغل أبيض ناعم": "برغل أبيض ناعم 1000غ",
        "برغل أبيض خشن": "برغل أبيض خشن 907غ",
        "- الأرز": "",
        "أرز أمريكي": "أرز أمريكي 907غ",
        "أرز إيطالي": "أرز إيطالي 907غ",
        "أرز مصري": "أرز مصري 907غ",
        "أرز ناعم": "أرز ناعم 1000غ",
        "أرز بسمتي": "أرز بسمتي 907غ",
        "أرز عنبري": "أرز عنبري 1000غ",
        "- السكر": "",
        "سكر أسمر": "سكر أسمر 1000غ",
        "سكر حب": "سكر حب 907غ",
        "سكر ناعم": "سكر ناعم 1000غ",
        "- الطحين": "",
        "طحين زيرو": "طحين زيرو 1000غ",
        "طحين غود ميدل": "طحين غود ميدل 1ك",
        "طحين غود مارك": "طحين غود مارك 907غ",
        "طحين فقش": "طحين فقش 1000غ",
        "طحين أسمر": "طحين أسمر 1000غ",
        "طحين ذرة": "طحين ذرة 1000غ",
        "طحين فرخة": "طحين فرخة 907غ",
        "سميد": "سميد 907غ",
        "- أصناف متنوعة": "",
        "قمح مقشور": "قمح مقشور 907غ",
        "ترمس حلو": "ترمس حلو 1000غ",
        "ترمس مر": "ترمس مر 1000غ",
        "ذرة بوشار": "ذرة بوشار 1000غ",
        "ذرة مجروشة": "ذرة مجروشة 1000غ",
        "مغربية": "مغربية 907غ",
        "كشك بلدي": "*كشك بلدي 1000غ",
        "فانيليا": "*فانيليا 1000غ",
        "باكنغ بودر": "*باكنغ بودر 1000غ",
        "نشاء ناعم": "نشاء ناعم 1000غ",
        "نشاء حب": "نشاء حب 1000غ",
        "كعك مطحون": "*كعك مطحون 1000غ",
        "فريك مجروش": "*فريك مجروش 1000غ"
    }

    g_sels = render_billing_items(items_1k, "g1k")

    if st.button("✅ تثبيت الحبوب"): st.session_state.cart.extend(g_sels); st.session_state.page = 'home'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة البهارات ---
elif st.session_state.page == 'spices':
    st.markdown('<div class="header-box"><h2>🌶️ نموذج البهارات</h2></div>', unsafe_allow_html=True)
    s_sels = []

    with st.expander("🌶️ بهارات 50 غ (دزينة *12)"):
        items_50g = {
            "بهار حلو": "*بهار حلو 50غ*12", "فلفل أسود": "*فلفل أسود 50غ*12", "فلفل أحمر": "*فلفل أحمر 50غ*12",
            "قرفة ناعمة": "*قرفة ناعمة 50غ*12", "سبع بهارات": "*سبع بهارات 50غ*12", "عقدة صفراء": "*عقدة صفراء 50غ*12",
            "كمون": "*كمون 50غ*12", "كزبرة": "*كزبرة 50غ*12", "يانسون": "*يانسون 50غ*12", "سماق": "*سماق 50غ*12",
            "- خلطات 50غ": "",
            "بهار دجاج": "*بهار دجاج 50غ*12", "طاووق": "*بهار طاووق 50غ*12", "فاهيتا": "*بهار فاهيتا 50غ*12",
            "شورما لحم": "*بهار شورما لحم 50غ*12", "شورما دجاج": "*بهار شورما دجا 50غ*12ج"
        }
        s_sels += render_billing_items(items_50g, "s50")

    with st.expander("🍃 بهارات 20 غ (دزينة *12)"):
        items_20g = {
            "جوزة الطيب": "*جوز الطيب ناعم 20غ*12", "محلب": "*محلب ناعم 20غ*12", "هال ناعم": "*هال ناعم 20غ*12",
            "قرنفل حب": "*قرنفل حب 20غ*12", "عصفر": "*عصفر 20غ*12"
        }
        s_sels += render_billing_items(items_20g, "s20")

    with st.expander("📦 بهارات 500 غ (بالحبة)"):
        items_500g = {
            "بهار حلو": "*بهار حلو 500غ", "فلفل أسود": "*فلفل أسود 500غ", "كمون": "*كمون 500غ",
            "قرفة عيدان": "*قرفة عيدان 500غ", "هال حب": "*هال حب 500غ"
        }
        s_sels += render_billing_items(items_500g, "s500")

    if st.button("✅ تثبيت البهارات"): st.session_state.cart.extend(s_sels); st.session_state.page = 'home'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة صنف خاص ---
elif st.session_state.page == 'special':
    st.markdown('<div class="header-box"><h2>📋 طلب صنف خاص</h2></div>', unsafe_allow_html=True)
    sp_i = st.text_input("اسم الصنف:")
    sp_q = st.text_input("العدد:")
    if st.button("✅ تثبيت"):
        if sp_i and sp_q:
            st.session_state.cart.append({"item": f"خاص: {sp_i}", "qty": ar_to_en_num(sp_q)})
            st.session_state.page = 'home'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()
