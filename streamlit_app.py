import streamlit as st
import urllib.parse

# إعدادات الصفحة
st.set_page_config(page_title="حلباوي إخوان - النظام المتكامل", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .category-header { 
        background-color: #e9ecef; color: #1E3A8A; padding: 8px; border-radius: 5px; 
        font-weight: bold; margin-top: 15px; border-right: 5px solid #fca311; text-align: right;
    }
    .item-box { 
        color: white !important; font-weight: bold !important; font-size: 16px !important; 
        background-color: #1E3A8A !important; padding: 8px; border-radius: 8px; text-align: right; width: 100%;
    }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; font-size: 18px !important; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 45px; width: 100%; }
    .review-panel { background-color: #1c212d; border: 2px solid #fca311; padding: 15px; border-radius: 10px; color: white; }
    </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'customer' not in st.session_state: st.session_state.customer = ""

RECEIVING_NUMBER = "9613220893"

def ar_to_en(text):
    return text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))

def render_items(items_dict, prefix):
    for disp, bill in items_dict.items():
        if disp.startswith("-"):
            st.markdown(f'<div class="category-header">{disp[1:]}</div>', unsafe_allow_html=True)
        else:
            col_txt, col_in = st.columns([3, 1])
            with col_txt: st.markdown(f'<div class="item-box">{disp}</div>', unsafe_allow_html=True)
            with col_in:
                # حل مشكلة التكرار باستخدام المفتاح التقني الفريد
                val = st.text_input("", key=f"{prefix}_{bill}", label_visibility="collapsed", placeholder="0")
                if val:
                    qty = ar_to_en(val)
                    if qty.isdigit() and int(qty) > 0:
                        st.session_state.cart[bill] = qty
                    elif qty == "0" and bill in st.session_state.cart:
                        del st.session_state.cart[bill]

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    st.session_state.customer = st.text_input("👤 اسم الزبون / المندوب:", st.session_state.customer)

    if st.session_state.cart:
        with st.container():
            st.markdown('<div class="review-panel"><h3>📋 مراجعة الطلبية (الأسماء التقنية):</h3>', unsafe_allow_html=True)
            for bill, qty in st.session_state.cart.items():
                st.write(f"✅ {bill} — الكمية: {qty}")
            
            if st.button("🚀 إرسال عبر واتساب"):
                if not st.session_state.customer:
                    st.error("الرجاء إدخال اسم الزبون!")
                else:
                    msg = f"طلبية: *{st.session_state.customer}*\n" + "="*15 + "\n"
                    for bill, qty in st.session_state.cart.items():
                        msg += f"{bill} : {qty}\n"
                    st.markdown(f'<a href="https://api.whatsapp.com/send?phone={RECEIVING_NUMBER}&text={urllib.parse.quote(msg)}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold;">تأكيد وفتح واتساب ✅</button></a>', unsafe_allow_html=True)
            
            if st.button("🗑️ مسح القائمة"):
                st.session_state.cart = {}; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("🌾 الحبوب"): st.session_state.page = 'grains_page'; st.rerun()
    with c2:
        if st.button("🌶️ البهارات"): st.session_state.page = 'spices_page'; st.rerun()
    with c3:
        if st.button("📋 صنف خاص"): st.session_state.page = 'special_page'; st.rerun()

# --- صفحة الحبوب (تفريغ الصور 2, 9, 10, 11) ---
elif st.session_state.page == 'grains_page':
    st.markdown('<div class="header-box"><h2>قائمة الحبوب الكاملة</h2></div>', unsafe_allow_html=True)
    
    grains_data = {
        "-حبوب 1000غ / 907غ": "",
        "حمص فحلي 12": "حمص فحلي\"12\"907غ", "حمص فحلي 9": "حمص فحلي\"9\"907غ", "حمص كسر": "حمص كسر 1000غ", #
        "فول حب": "فول حب 1000غ", "فول مجروش": "فول مجروش 1000غ", "فول عريض": "فول عريض 1000غ", #
        "فاصوليا صنوبرية": "فاصوليا صنوبرية 907غ", "فاصوليا حمرا طويلة": "فاصوليا حمرا طويلة 1000غ", #
        "فاصوليا عريضة": "فاصوليا عريضة 1000غ", "عدس أبيض بلدي": "عدس أبيض بلدي 907غ", #
        "أرز إيطالي": "أرز إيطالي 907غ", "أرز بسمتي": "أرز بسمتي 907غ", "طحين زيرو": "طحين زيرو 1000غ", #
        "طحين غود ميدل": "طحين غود ميدل1ك", "سميد": "سميد 907غ", "ترمس حلو": "ترمس حلو 1000غ", #
        "كشك بلدي": "*كشك بلدي 1000غ", "فانيليا": "*فانيليا 1000غ", "باكنغ بودر": "*باكنغ بودر 1000غ", #
        "مغربية": "مغربية 907غ*", #
        
        "-قسم 500غ / 454غ / 200غ": "",
        "فاصوليا عريضة 500غ": "فاصوليا عريضة500غ", "فول عريض 500غ": "فول عريض500غ", "كاكاو 500غ": "*كاكاو500غ", #
        "ترمس حلو 500غ": "ترمس حلو500غ", "ذرة بوشار 454غ": "ذرة بوشار454غ", "شوفان مبروش 500غ": "شوفان مبروش500غ", #
        "كشك بلدي 500غ": "*كشك بلدي 500غ", "سكر ناعم 500غ": "سكر ناعم500غ", "سكر نبات 500غ": "*سكر نبات*500غ", #
        "زعتر محوج 500غ": "زعتر محوج* 500غ", "ملوخية 200غ": "ملوخية 200غ", "بامية زهرة 200غ": "بامية زهرة 200غ", #
        "برش جوز الهند 200غ": "برش جوز الهند 200غ", "نشاء ناعم 200غ": "نشاء ناعم 200غ", #
        "كشك بلدي 200غ": "*كشك بلدي 200غ", "فلافل جاهزة علب": "*فلافل جاهزة \"علب\"", #
        "سكر نبات 200غ": "سكر نبات* 200غ", "سكر نبات 100غ": "سكر نبات* 100غ" #
    }
    render_items(grains_data, "GR")
    if st.button("🔙 حفظ والعودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة البهارات (تفريغ الصور 1, 5, 6, 7, 8) ---
elif st.session_state.page == 'spices_page':
    st.markdown('<div class="header-box"><h2>قائمة البهارات الشاملة</h2></div>', unsafe_allow_html=True)
    
    with st.expander("🌶️ بهارات 50غ (بالدزينة)", expanded=True):
        sp_50 = {
            "بهار حلو": "*بهار حلو 50غ*12", "فلفل أسود": "*فلفل أسود 50غ*12", "قرفة ناعمة": "*قرفة ناعمه 50غ*12", #
            "سبع بهارات": "*سبع بهارات 50غ*12", "عقدة صفرة": "*عقدة صفرة50غ*12", "كمون": "*كمون 50غ*12", #
            "بهار دجاج": "*بهار دجاج 50غ*12", "بهار طاووق": "*بهار طاووق 50غ*12", "بهار بيتزا": "*بهار بيتزا 50غ*12", #
            "بهار شورما لحم": "*بهار شورما لحم 50غ*12", "بهار شورما دجاج": "*بهار شورما دجا 50غ*12ج", #
            "فليفلة حلوة": "*فليفلة حلوة 50غ*12", #
            "خلطة حلباوي المميزة": "*خلطة حلباوي المميزة 50غ*12", "بهار مكسيكانا": "*بهار مكسيكانا 50غ*12", #
            "بهار كبسة": "*بهار كبسة 50غ*12", "بهار صيني": "*بهار صيني 50غ*12", #
            "-أصناف حب 50غ": "",
            "بهار حلو حب": "*بهار حلو حب 50غ*12", "فلفل أسود حب": "*فلفل أسود حب 50غ*12", "يانسون حب": "*يانسون حب 50غ*12", #
            "كمون حب": "*كمون حب 50غ*12", "كزبرة حب": "*كزبرة حب 50غ*12", "حبة البركة حب": "*حبة البركة حب 50غ*12" #
        }
        render_items(sp_50, "SP50")

    with st.expander("🍃 بهارات 20غ (بالدزينة)"):
        sp_20 = {
            "جوز الطيب ناعم": "*جوز الطيب ناعم 20غ*12", "محلب ناعم": "*محلب ناعم 20غ*12", "نعنع يابس": "*نعنع يابس 20غ*12", #
            "مردكوش": "*مردكوش 20غ*12", "قرنفل ناعم": "*قرنفل ناعم 20غ*12", "بهار أبيض ناعم": "*بهار أبيض ناعم 20غ*12", #
            "هال ناعم": "*هال ناعم 20غ*12", "زنجبيل ناعم": "*زنجبيل ناعم 20غ*12", "عصفر": "*عصفر 20غ*12", #
            "هال حب": "*هال حب 20غ*12", "قرنفل حب": "*قرنفل حب 20غ*12", "محلب حب": "*محلب حب 20غ*12" #
        }
        render_items(sp_20, "SP20")

    with st.expander("🌿 بهارات 500غ"):
        sp_500 = {
            "بهار حلو 500": "*بهار حلو 500غ", "فلفل أسود 500": "*فلفل أسود 500غ", "سبع بهارات 500": "*سبع بهارات 500غ", #
            "عقدة صفرة 500": "*عقدة صفرة 500غ", "كمون ناعم 500": "كمون ناعم 500غ*", "بهار أرز 500": "*بهار أرز 500غ", #
            "ثوم مجفف 500": "ثوم مجفف 500غ", "بصل مجفف بودرة 500": "*بصل مجفف بودرة 500غ", "بهار فلافل 500": "*بهار فلافل 500غ", #
            "بهار كبسة 500": "*بهار كبسة 500غ", "بهار همبرغر 500": "*بهار همبرغر 500غ", "بهار دجاج 500": "*بهار دجاج 500غ", #
            "بهار أبيض 500": "*بهار أبيض 500غ", "بهار طاووق 500": "*بهار طاووق 500غ" #
        }
        render_items(sp_500, "SP500")
        
    if st.button("🔙 حفظ والعودة"): st.session_state.page = 'home'; st.rerun()

# --- صفحة صنف خاص ---
elif st.session_state.page == 'special_page':
    st.markdown('<div class="header-box"><h2>📋 بضاعة حسب الطلب</h2></div>', unsafe_allow_html=True)
    sp_name = st.text_input("اسم الصنف:")
    sp_pack = st.text_input("التعبئة:")
    sp_qty = st.text_input("الكمية:")
    if st.button("✅ إضافة"):
        if sp_name and sp_qty:
            bill_name = f"طلب خاص: {sp_name} ({sp_pack})"
            st.session_state.cart[bill_name] = ar_to_en(sp_qty)
            st.success("تمت الإضافة")
            st.session_state.page = 'home'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()
