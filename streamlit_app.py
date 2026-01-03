import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="طلبيات حلباوي", layout="wide")

# 2. الرابط المباشر للبيانات
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

# 3. التصميم (الألوان والكبسات)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .main-header { background-color: #1E3A8A; text-align: center; padding: 20px; border-radius: 10px; border-bottom: 5px solid #fca311; margin-bottom: 25px; }
    .stExpander { border: 1px solid #2d3748 !important; background-color: #1c2333 !important; border-radius: 10px !important; margin-bottom: 10px !important; }
    .sub-category-header { background-color: #2d3748; color: #fca311; padding: 5px 15px; border-radius: 5px; font-weight: bold; margin-top: 15px; margin-bottom: 10px; border-right: 5px solid #fca311; text-align: right; }
    .item-label { background-color: #1E3A8A; color: white; padding: 10px; border-radius: 5px; font-weight: bold; text-align: right; font-size: 1rem; margin-bottom: 5px; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; height: 45px !important; border-radius: 5px !important; }
    /* زر التثبيت والمراجعة الأخضر */
    .review-btn button { background-color: #28a745 !important; color: white !important; border: none; }
    /* زر الإرسال البرتقالي */
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; border-radius: 10px; height: 55px; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is not None:
    # --- الصفحة الرئيسية ---
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        cust_name = st.text_input("👤 اسم المندوب / الزبون:", key="main_cust")
        
        st.write("### 📂 الأقسام الرئيسية:")
        for c in df['cat'].unique():
            if st.button(f"📦 قسم {c}", use_container_width=True):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()

    # --- صفحة التفاصيل ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="main-header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        col_back, col_rev = st.columns(2)
        with col_back:
            if st.button("🔙 عودة للقائمة"):
                st.session_state.page = 'home'
                st.rerun()
        
        # --- كبسة التثبيت والمراجعة داخل القسم ---
        with col_rev:
            with st.popover("📋 مراجعة وتثبيت"):
                st.write("### الأصناف التي اخترتها:")
                current_order = {k: v for k, v in st.session_state.cart.items() if v}
                if not current_order:
                    st.write("السلة فارغة حالياً")
                else:
                    for item, qty in current_order.items():
                        st.write(f"✅ {item}: **{qty}**")
                    
                    st.divider()
                    cust = st.session_state.get('main_cust', "")
                    if st.button("🚀 إرسال الطلبية الآن"):
                        if cust:
                            msg = f"طلبية {cat}\nالزبون: {cust}\n" + "\n".join([f"- {i}: {q}" for i, q in current_order.items()])
                            url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                            st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">تأكيد وفتح واتساب ✅</button></a>', unsafe_allow_html=True)
                        else:
                            st.error("يرجى كتابة اسم الزبون في الصفحة الرئيسية")

        st.divider()

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
                            curr_val = st.session_state.cart.get(f"{row['name']} ({row['pack']})", "")
                            val = st.text_input("", value=curr_val, key=key, label_visibility="collapsed")
                            if val:
                                st.session_state.cart[f"{row['name']} ({row['pack']})"] = val
