import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# الرابط مع إضافة رمز إجباري للتحديث
DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRMNeseeCy7logkwged_RZRu83VH3KXOHBurgahfwyi_LjGfd2CmD9-Mt-tCAO4C3xT8LWOIZaTUrX/pub?gid=283264234&single=true&output=csv&cache=0"

@st.cache_data(ttl=2) # تحديث كل ثانيتين فقط
def load_data():
    try:
        # قراءة البيانات مع تجاهل التخزين المؤقت
        df = pd.read_csv(DB_URL, header=None).dropna(how='all')
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except:
        return None

df = load_data()

# تصميم الهاتف السريع
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 10px; border-bottom: 4px solid #fca311; }
    .item-card { background-color: #1c2333; padding: 12px; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 8px; text-align: right; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; width: 100%; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is None or df.empty:
    st.error("⚠️ لا تزال البيانات غير ظاهرة. جرب فتح الرابط في متصفحك للتأكد.")
    if st.button("🔄 محاولة التحديث الآن"):
        st.cache_data.clear()
        st.rerun()
else:
    if st.session_state.page == 'home':
        st.markdown('<div class="header"><h1>طلبيات حلباوي</h1></div>', unsafe_allow_html=True)
        cats = df['cat'].unique()
        for c in cats:
            if st.button(f"📦 {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
                
        if st.session_state.cart:
            st.divider()
            cust = st.text_input("👤 اسم الزبون:")
            if st.button("✅ إرسال عبر واتساب"):
                msg = f"طلبية: {cust}\n" + "\n".join([f"{k}: {v}" for k, v in st.session_state.cart.items()])
                url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank">تأكيد واتساب</a>', unsafe_allow_html=True)

    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        filtered = df[df['cat'] == cat]
        for _, row in filtered.iterrows():
            c1, c2 = st.columns([3, 1])
            with c1: st.markdown(f'<div class="item-card">{row["name"]}</div>', unsafe_allow_html=True)
            with c2:
                key = f"q_{row['sci']}_{row['pack']}"
                val = st.text_input("", key=key, label_visibility="collapsed")
                if val and val.isdigit(): st.session_state.cart[row['sci']] = val
        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()
