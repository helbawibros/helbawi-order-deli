import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="طلبيات حلباوي", layout="wide")

# 2. جلب البيانات
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
SHEET_NAME = "طلبات"
DIRECT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(DIRECT_URL, header=None).dropna(how='all')
        df = df.iloc[:, :5]
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except:
        return None

df = load_data()

# 3. التصميم والألوان
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .main-header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 10px; border-bottom: 5px solid #fca311; margin-bottom: 20px; }
    .sub-category-header { background-color: #2d3748; color: #fca311; padding: 5px; border-radius: 5px; font-weight: bold; margin-top: 10px; text-align: right; border-right: 5px solid #fca311; }
    .item-label { background-color: #1E3A8A; color: white; padding: 10px; border-radius: 5px; font-weight: bold; text-align: right; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; border-radius: 10px; height: 50px; width: 100%; }
    .fixed-footer { position: fixed; bottom: 0; left: 0; width: 100%; background-color: #1E3A8A; padding: 10px; text-align: center; border-top: 3px solid #fca311; z-index: 1000; }
    </style>
    """, unsafe_allow_html=True)

# تهيئة المخزن (السلة)
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cust_name' not in st.session_state: st.session_state.cust_name = ""

if df is not None:
    # --- القائمة الجانبية للتنقل الدائم ---
    with st.sidebar:
        st.markdown("### 📋 التحكم")
        if st.button("🏠 القائمة الرئيسية"):
            st.session_state.page = 'home'
            st.rerun()
        if st.button("🛒 مراجعة الطلبية كاملة"):
            st.session_state.page = 'review'
            st.rerun()
        st.divider()
        st.session_state.cust_name = st.text_input("👤 اسم الزبون:", value=st.session_state.cust_name)

    # --- الصفحة الرئيسية (الأقسام) ---
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        st.write("### 📂 اختر القسم لتعبئة الأصناف:")
        cols = st.columns(2)
        for idx, c in enumerate(df['cat'].unique()):
            with cols[idx % 2]:
                if st.button(f"📦 {c}"):
                    st.session_state.sel_cat = c
                    st.session_state.page = 'details'
                    st.rerun()

    # --- صفحة التفاصيل (داخل القسم) ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="main-header"><h2>قسم {cat}</h2></div>', unsafe_allow_html=True)
        
        # زر التثبيت والمراجعة في كل صفحة قسم
        if st.button("✅ تثبيت ومراجعة الطلب الكامل"):
            st.session_state.page = 'review'
            st.rerun()

        cat_df = df[df['cat'] == cat]
        for weight in cat_df['pack'].unique():
            with st.expander(f"🔽 {weight}"):
                w_df = cat_df[cat_df['pack'] == weight]
                for sub in w_df['sub'].unique():
                    st.markdown(f'<div class="sub-category-header">{sub}</div>', unsafe_allow_html=True)
                    items = w_df[w_df['sub'] == sub]
                    for _, row in items.iterrows():
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f'<div class="item-label">{row["name"]}</div>', unsafe_allow_html=True)
                        with c2:
                            key = f"q_{row['name']}_{row['pack']}"
                            curr = st.session_state.cart.get(key, {}).get('qty', "")
                            val = st.text_input("", value=curr, key=key+"_in", label_visibility="collapsed")
                            if val:
                                # تخزين اسم الصنف (D) والكمية فقط
                                st.session_state.cart[key] = {'name': row['name'], 'qty': val}
                            elif val == "" and key in st.session_state.cart:
                                del st.session_state.cart[key]

    # --- صفحة المراجعة النهائية (تجمع كل الأقسام) ---
    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>مراجعة الطلبية الكاملة</h1></div>', unsafe_allow_html=True)
        
        if not st.session_state.cart:
            st.warning("السلة فارغة، لم يتم اختيار أي أصناف بعد.")
            if st.button("🔙 العودة للأقسام"):
                st.session_state.page = 'home'
                st.rerun()
        else:
            st.write(f"👤 **الزبون:** {st.session_state.cust_name}")
            st.write("---")
            
            final_list = []
            for k, v in st.session_state.cart.items():
                if v['qty'].isdigit() and int(v['qty']) > 0:
                    st.markdown(f"🔹 **{v['name']}** ← الكمية: `{v['qty']}`")
                    final_list.append(f"{v['name']}: {v['qty']}")
            
            st.divider()
            
            if st.button("🚀 إرسال الطلبية كاملة عبر واتساب"):
                if st.session_state.cust_name:
                    msg = f"طلبية الزبون: {st.session_state.cust_name}\n" + "\n".join(final_list)
                    url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">تأكيد وفتح واتساب ✅</button></a>', unsafe_allow_html=True)
                else:
                    st.error("الرجاء إدخال اسم الزبون قبل الإرسال")
            
            if st.button("➕ إضافة المزيد من الأصناف"):
                st.session_state.page = 'home'
                st.rerun()

