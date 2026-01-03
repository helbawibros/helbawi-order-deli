import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# الرابط الخاص بك
DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRMNeseeCy7logkwged_RZRu83VH3KXOHBurgahfwyi_LjGfd2CmD9-Mt-tCAO4C3xT8LWOIZaTUrX/pub?gid=283264234&single=true&output=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        # قراءة البيانات مباشرة بعد تعديلك للسطر الأول
        df = pd.read_csv(DB_URL, header=None).dropna(how='all')
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except:
        return None

df = load_data()

# تنسيق واجهة الهاتف
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

if df is None:
    st.warning("⚠️ جوجل يقوم بتحديث الرابط بعد تعديلك الأخير. يرجى الانتظار دقيقة وعمل Refresh.")
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
                st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold;">تأكيد الطلبية</button></a>', unsafe_allow_html=True)

    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        filtered = df[df['cat'] == cat]
        for sub in filtered['sub'].unique():
            st.markdown(f"🔹 **{sub}**")
            sub_df = filtered[filtered['sub'] == sub]
            for _, row in sub_df.iterrows():
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown(f'<div class="item-card">{row["name"]} ({row["pack"]})</div>', unsafe_allow_html=True)
                with c2:
                    # مفتاح فريد لمنع خطأ التكرار Duplicate Key
                    key = f"q_{row['sci']}_{row['pack']}"
                    val = st.text_input("", key=key, label_visibility="collapsed")
                    if val and val.isdigit() and int(val) > 0:
                        st.session_state.cart[row['sci']] = val

        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()
