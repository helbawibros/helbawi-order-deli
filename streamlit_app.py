import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعداد الرابط المباشر للملف (تعديل الرابط ليقوم بتصدير CSV فورياً)
# الرابط الذي أرسلته ينتهي بـ /edit، قمت بتحويله إلى /export ليعمل مع البرنامج
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
DIRECT_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=283264234"

# 2. إعدادات الصفحة
st.set_page_config(page_title="حلباوي إخوان - الطلبيات", layout="wide")

# 3. وظيفة جلب البيانات مع تحديث فوري (ttl=1)
@st.cache_data(ttl=1)
def load_live_data():
    try:
        # قراءة البيانات مع تسمية الأعمدة بناءً على ترتيب ملفك (A, B, C, D, E)
        df = pd.read_csv(DIRECT_CSV_URL, header=None).dropna(how='all')
        df.columns = ['cat', 'pack', 'sub', 'display_name', 'scientific_name']
        return df
    except Exception as e:
        return None

df = load_live_data()

# 4. تصميم الواجهة للهاتف (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .header-box { background-color: #1E3A8A; text-align: center; padding: 20px; border-radius: 12px; border-bottom: 5px solid #fca311; margin-bottom: 20px; }
    .category-title { font-size: 1.5rem; color: #fca311; text-align: center; margin-bottom: 15px; }
    .item-row { background-color: #1c2333; padding: 15px; border-radius: 10px; border: 1px solid #2d3748; margin-bottom: 10px; }
    .item-name { font-size: 1.1rem; font-weight: bold; text-align: right; color: #ffffff; }
    .item-pack { font-size: 0.9rem; color: #718096; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; font-size: 1.2rem !important; text-align: center !important; border-radius: 5px !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; width: 100%; height: 50px; border-radius: 10px; border: none; }
    .footer { text-align: center; color: #4a5568; font-size: 0.8rem; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# 5. إدارة حالة التطبيق (السلة والصفحات)
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية (الأقسام) ---
if st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    
    if df is not None:
        st.write("### 📂 اختر القسم:")
        # جلب الأقسام الفريدة من العمود A
        categories = df['cat'].unique()
        for cat in categories:
            if st.button(f"📦 {cat}", use_container_width=True):
                st.session_state.selected_cat = cat
                st.session_state.page = 'details'
                st.rerun()
    else:
        st.error("⚠️ فشل الاتصال بملف الأكسل. تأكد أن الملف متاح لـ 'Anyone with the link'.")

    # عرض السلة إذا كانت تحتوي على أصناف
    if st.session_state.cart:
        st.markdown("---")
        with st.expander("🛒 مراجعة السلة وإرسال الطلب", expanded=True):
            for name, qty in list(st.session_state.cart.items()):
                st.write(f"✅ **{name}** ← الكمية: `{qty}`")
            
            customer_name = st.text_input("👤 اسم المندوب / الزبون:")
            if st.button("🚀 تأكيد وإرسال عبر واتساب"):
                if not customer_name:
                    st.warning("الرجاء كتابة اسم الزبون أولاً!")
                else:
                    # تحضير نص الرسالة
                    order_text = f"طلبية من: *{customer_name}*\n" + "—"*15 + "\n"
                    for item, q in st.session_state.cart.items():
                        order_text += f"• {item}: {q}\n"
                    
                    # رابط واتساب (رقمك المعتمد)
                    wa_url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(order_text)}"
                    st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">فتح واتساب الآن ✅</button></a>', unsafe_allow_html=True)
            
            if st.button("🗑️ تفريغ السلة"):
                st.session_state.cart = {}
                st.rerun()

# --- صفحة تفاصيل القسم ---
elif st.session_state.page == 'details':
    current_cat = st.session_state.selected_cat
    st.markdown(f'<div class="header-box"><h2>قسم {current_cat}</h2></div>', unsafe_allow_html=True)
    
    # تصفية البيانات حسب القسم المختار
    cat_items = df[df['cat'] == current_cat]
    
    # عرض حسب العناوين الفرعية (العمود C)
    for sub_title in cat_items['sub'].unique():
        st.markdown(f'<div class="category-title">🔹 {sub_title}</div>', unsafe_allow_html=True)
        sub_df = cat_items[cat_items['sub'] == sub_title]
        
        for _, row in sub_df.iterrows():
            with st.container():
                col_info, col_qty = st.columns([3, 1])
                with col_info:
                    st.markdown(f"""
                    <div class="item-row">
                        <div class="item-name">{row['display_name']}</div>
                        <div class="item-pack">{row['pack']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_qty:
                    # استخدام الاسم العلمي (العمود E) كمفتاح فريد لمنع الأخطاء
                    unique_key = f"input_{row['scientific_name']}_{row['pack']}"
                    # جلب الكمية المخزنة سابقاً إن وجدت
                    current_qty = st.session_state.cart.get(row['scientific_name'], "")
                    
                    val = st.text_input("", value=current_qty, key=unique_key, label_visibility="collapsed", placeholder="0")
                    
                    # تحديث السلة تلقائياً عند الإدخال
                    if val and val.isdigit() and int(val) > 0:
                        st.session_state.cart[row['scientific_name']] = val
                    elif val == "0" and row['scientific_name'] in st.session_state.cart:
                        del st.session_state.cart[row['scientific_name']]

    if st.button("🔙 عودة للقائمة الرئيسية"):
        st.session_state.page = 'home'
        st.rerun()

st.markdown('<div class="footer">نظام طلبات حلباوي إخوان © 2026</div>', unsafe_allow_html=True)

