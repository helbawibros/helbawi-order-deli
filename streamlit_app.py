import streamlit as st
import pandas as pd
import urllib.parse

# إعدادات الصفحة
st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# 1. الرابط المباشر المحدث بناءً على صورك
# قمت باستخراج الـ ID الصحيح من لقطة الشاشة الخاصة بك
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"

# سنستخدم رابطاً عاماً يسحب الورقة الأولى تلقائياً لتجنب خطأ الـ GID
DIRECT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=1)
def load_data():
    try:
        # قراءة البيانات مباشرة
        df = pd.read_csv(DIRECT_URL, header=None).dropna(how='all')
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except Exception as e:
        return None

df = load_data()

# تصميم واجهة الهاتف
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 10px; border-bottom: 5px solid #fca311; margin-bottom: 20px; }
    .item-card { background-color: #1c2333; padding: 12px; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 8px; text-align: right; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; width: 100%; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

# التحقق من البيانات
if df is None or df.empty:
    st.error("⚠️ فشل في سحب البيانات.")
    st.info("تأكد من فتح الرابط في متصفحك مرة واحدة لتنشيطه من طرف جوجل.")
    if st.button("🔄 محاولة تحديث الاتصال"):
        st.cache_data.clear()
        st.rerun()
else:
    # --- الصفحة الرئيسية ---
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
                st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold;">تأكيد وفتح واتساب</button></a>', unsafe_allow_html=True)

    # --- صفحة المنتجات ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        filtered = df[df['cat'] == cat]
        for _, row in filtered.iterrows():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f'<div class="item-card">{row["name"]} ({row["pack"]})</div>', unsafe_allow_html=True)
            with c2:
                key = f"q_{row['sci']}_{row['pack']}"
                current = st.session_state.cart.get(row['name'], "")
                val = st.text_input("", value=current, key=key, label_visibility="collapsed")
                if val and val.isdigit() and int(val) > 0:
                    st.session_state.cart[row['name']] = val
                elif val == "0" and row['name'] in st.session_state.cart:
                    del st.session_state.cart[row['name']]

        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()
