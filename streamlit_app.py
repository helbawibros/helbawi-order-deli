import streamlit as st
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="شركة حلباوي إخوان - نظام الطلبيات", layout="wide")

# 2. تصميم الواجهة (نفس الروح مع تحسينات طفيفة للوضوح)
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
        padding: 5px 12px; border-radius: 8px; text-align: right; min-width: 140px; width: 100%;
    }
    input { 
        background-color: #ffffcc !important; color: black !important; font-weight: bold !important; 
        height: 40px !important; font-size: 20px !important;
    }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 50px; }
    .review-card { background-color: #1c212d; border: 1px solid #fca311; padding: 15px; border-radius: 10px; color: white; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# إدارة الحالة
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cart' not in st.session_state: st.session_state.cart = []
if 'customer' not in st.session_state: st.session_state.customer = ""

RECEIVING_NUMBER = "9613220893"

def ar_to_en_num(text):
    return text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))

# دالة العرض المزدوج (اسم للمندوب واسم للسيستم)
def render_list_dual(items_dict, key_suffix):
    for display_name, billing_name in items_dict.items():
        if display_name.startswith("-"):
            st.markdown(f'<div class="category-header">{display_name[1:]}</div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns([2.5, 1])
            with c1: st.markdown(f'<div class="item-box">{display_name}</div>', unsafe_allow_html=True)
            with c2:
                q = st.text_input("", key=f"{key_suffix}_{display_name}", label_visibility="collapsed", placeholder="0")
                if q:
                    en_q = ar_to_en_num(q)
                    if en_q.isdigit() and int(en_q) > 0:
                        # نبحث إذا كان الصنف موجود مسبقاً في السلة لتحديثه
                        st.session_state.cart = [i for i in st.session_state.cart if i['bill'] != billing_name]
                        st.session_state.cart.append({"disp": display_name, "bill": billing_name, "qty": en_q})

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.image("https://raw.githubusercontent.com/helbawibros/-/main/Logo%20.JPG", use_container_width=True)
    st.markdown('<div class="header-box"><h1>نظام طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    
    st.session_state.customer = st.text_input("👤 إسم الزبون / المندوب:", st.session_state.customer)

    # مراجعة الطلبية قبل الإرسال
    if st.session_state.cart:
        st.markdown('<div class="review-card"><h3>📋 مراجعة الطلبية:</h3>', unsafe_allow_html=True)
        for item in st.session_state.cart:
            st.write(f"• {item['disp']} ({item['qty']})")
        
        if st.button("🚀 إرسال الطلب النهائي عبر واتساب"):
            if not st.session_state.customer:
                st.error("الرجاء إدخال اسم الزبون أولاً!")
            else:
                msg = f"طلبية مبيعات: *{st.session_state.customer}*\n" + "-"*20 + "\n"
                for item in st.session_state.cart:
                    msg += f"{item['bill']} : {item['qty']}\n"
                st.markdown(f'<a href="https://api.whatsapp.com/send?phone={RECEIVING_NUMBER}&text={urllib.parse.quote(msg)}" target="_blank" style="background:#25d366;color:white;padding:15px;display:block;text-align:center;text-decoration:none;border-radius:10px;font-weight:bold;">تأكيد الإرسال لواتساب ✅</a>', unsafe_allow_html=True)
        
        if st.button("🗑️ مسح الطلبية بالكامل"):
            st.session_state.cart = []; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌾 الحبوب", use_container_width=True): st.session_state.page = 'grains'; st.rerun()
    with col2:
        if st.button("🌶️ البهارات", use_container_width=True): st.session_state.page = 'spices'; st.rerun()
    with col3:
        if st.button("📋 صنف خاص", use_container_width=True): st.session_state.page = 'special'; st.rerun()

# --- نموذج الحبوب ---
elif st.session_state.page == 'grains':
    st.markdown('<div class="header-box"><h2>نموذج الحبوب (1000غ/907غ)</h2></div>', unsafe_allow_html=True)
    
    grains_data = {
        "-الحمص": "",
        "حمص فحلي 12": "حمص فحلي\"12\"907غ", "حمص فحلي 9": "حمص فحلي\"9\"907غ", "حمص كسر": "حمص كسر 1000غ",
        "-الفول": "",
        "فول حب": "فول حب 1000غ", "فول مجروش": "فول مجروش 1000غ", "فول عريض": "فول عريض 1000غ",
        "-فاصوليا": "",
        "فاصوليا صنوبرية": "فاصوليا صنوبرية 907غ", "فاصوليا حمرا طويلة": "فاصوليا حمرا طويلة 1000غ", "فاصوليا حمرا مدعبلة": "فاصوليا حمرا مدعبلة 1000غ", "فاصوليا عريضة": "فاصوليا عريضة 1000غ",
        "-عدس": "",
        "عدس أبيض بلدي": "عدس أبيض بلدي 907غ", "عدس أحمر": "عدس أحمر 907غ", "عدس أحمر موردي": "عدس أحمر موردي 1000غ", "عدس عريض": "عدس عريض 907غ", "عدس مجروش": "عدس مجروش 907غ",
        "-برغل": "",
        "برغل أسمر ناعم": "برغل أسمر ناعم 907غ", "برغل أسمر خشن": "برغل أسمر خشن 907غ", "برغل أبيض ناعم": "برغل أبيض ناعم 1000غ", "برغل أبيض خشن": "برغل أبيض خشن 907غ",
        "-أرز": "",
        "أرز أمريكي": "أرز أمريكي 907غ", "أرز إيطالي": "أرز إيطالي 907غ", "أرز مصري": "أرز مصري 907غ", "أرز ناعم": "أرز ناعم 1000غ", "أرز بسمتي": "أرز بسمتي 907غ", "أرز عنبري": "أرز عنبري 1000غ",
        "-طحين وسميد": "",
        "طحين زيرو": "طحين زيرو 1000غ", "طحين غود ميدل": "طحين غود ميدل 1ك", "طحين غود مارك": "طحين غود مارك 907غ", "طحين فقش": "طحين فقش 1000غ", "طحين أسمر": "طحين أسمر 1000غ", "طحين فرخة": "طحين فرخة 907غ", "سميد": "سميد 907غ",
        "-متفرقات": "",
        "كشك بلدي": "*كشك بلدي 1000غ", "فانيليا": "*فانيليا 1000غ", "باكنغ بودر": "*باكنغ بودر 1000غ", "نشاء ناعم": "نشاء ناعم 1000غ", "كعك مطحون": "*كعك مطحون 1000غ", "فريك مجروش": "*فريك مجروش 1000غ", "ذرة بوشار": "ذرة بوشار 1000غ"
    }
    
    render_list_dual(grains_data, "gr")
    if st.button("🔙 حفظ والعودة للمراجعة"): st.session_state.page = 'home'; st.rerun()

# --- نموذج البهارات ---
elif st.session_state.page == 'spices':
    st.markdown('<div class="header-box"><h2>نموذج البهارات (بالدزينة)</h2></div>', unsafe_allow_html=True)
    
    with st.expander("🌶️ بهارات 50غ (الأسماء التقنية)", expanded=True):
        sp_50_data = {
            "بهار حلو": "*بهار حلو 50غ*12", "فلفل أسود": "*فلفل أسود 50غ*12", "فلفل أحمر": "*فلفل أحمر 50غ*12",
            "قرفة ناعمة": "*قرفة ناعمة 50غ*12", "سبع بهارات": "*سبع بهارات 50غ*12", "عقدة صفرة": "*عقدة صفرة 50غ*12",
            "كمون": "*كمون 50غ*12", "كزبرة": "*كزبرة 50غ*12", "يانسون": "*يانسون 50غ*12", "سماق": "*سماق 50غ*12",
            "بهار دجاج": "*بهار دجاج 50غ*12", "بهار طاووق": "*بهار طاووق 50غ*12", "بهار كبسة": "*بهار كبسة 50غ*12",
            "بهار شورما لحم": "*بهار شورما لحم 50غ*12", "بهار شورما دجا": "*بهار شورما دجا 50غ*12ج",
            "بهار مدخن": "*بهار مدخن 50غ*12", "بابريكا مدخن": "*بابريكا مدخن 50غ*12",
            "حبق": "*حبق 50غ*12", "لوما": "*لوما 50غ*12", "ورق غار": "*ورق غار 50غ*12"
        }
        render_list_dual(sp_50_data, "s50")

    with st.expander("🍃 بهارات 20غ"):
        sp_20_data = {
            "جوز الطيب ناعم": "*جوز الطيب ناعم 20غ*12", "محلب ناعم": "*محلب ناعم 20غ*12", "هال ناعم": "*هال ناعم 20غ*12",
            "قرنفل ناعم": "*قرنفل ناعم 20غ*12", "زنجبيل ناعم": "*زنجبيل ناعم 20غ*12", "عصفر": "*عصفر 20غ*12"
        }
        render_list_dual(sp_20_data, "s20")

    if st.button("🔙 حفظ والعودة للمراجعة"): st.session_state.page = 'home'; st.rerun()

# --- نموذج صنف خاص ---
elif st.session_state.page == 'special':
    st.markdown('<div class="header-box"><h2>📋 صنف بضاعة حسب الطلب</h2></div>', unsafe_allow_html=True)
    sp_name = st.text_input("اسم الصنف:")
    sp_pack = st.text_input("نوع التعبئة (مثلاً 500غ):")
    sp_qty = st.text_input("الكمية:")
    
    if st.button("✅ إضافة الصنف الخاص"):
        if sp_name and sp_qty:
            full_special_name = f"{sp_name} ({sp_pack})"
            st.session_state.cart.append({"disp": full_special_name, "bill": f"خاص: {full_special_name}", "qty": ar_to_en_num(sp_qty)})
            st.success(f"تمت إضافة {sp_name}")
            st.session_state.page = 'home'; st.rerun()
    if st.button("🔙 عودة"): st.session_state.page = 'home'; st.rerun()
