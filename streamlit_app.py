import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# 2. الرابط المباشر لورقة "طلبات"
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=طلبات"

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(URL, header=None).dropna(how='all')
        df.columns = ['القسم', 'الوزن', 'الفئة', 'الاسم', 'العلمي']
        return df
    except:
        return None

df = load_data()

# 3. تنسيق الواجهة (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .header-box { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 12px; border-bottom: 4px solid #fca311; }
    .weight-title { background-color: #fca311; color: #1E3A8A; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 20px; text-align: center; }
    .sub-cat { color: #fca311; font-weight: bold; margin-top: 15px; border-right: 4px solid #fca311; padding-right: 10px; }
    .item-card { background-color: #1c2333; padding: 12px; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 8px; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; }
    .stButton button { border-radius: 10px; height: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is not None:
    # --- الصفحة الرئيسية ---
    if st.session_state.page == 'home':
        st.markdown('<div class="header-box"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        # محرك البحث
        search = st.text_input("🔍 ابحث عن صنف مباشرة (مثلاً: حمص):")
        if search:
            res = df[df['الاسم'].str.contains(search, na=False)]
            for _, r in res.iterrows():
                st.markdown(f'<div class="item-card">{r["الاسم"]} ({r["الوزن"]})</div>', unsafe_allow_html=True)
                q = st.text_input("الكمية", key=f"s_{r['العلمي']}_{r['الوزن']}", label_visibility="collapsed")
                if q: st.session_state.cart[f"{r['الاسم']} ({r['الوزن']})"] = q
        else:
            st.write("### 📂 الأقسام الرئيسية")
            for cat in df['القسم'].unique():
                if st.button(f"📦 {cat}", use_container_width=True):
                    st.session_state.sel_cat = cat
                    st.session_state.page = 'details'
                    st.rerun()

        # زر المشاهدة والتثبيت
        if st.session_state.cart:
            st.divider()
            with st.expander("🛒 عرض السلة وتثبيت الطلب", expanded=True):
                for k, v in list(st.session_state.cart.items()):
                    st.write(f"✅ {k}: **{v}**")
                
                cust = st.text_input("👤 اسم المندوب/الزبون:")
                if st.button("🚀 تثبيت وإرسال واتساب", type="primary", use_container_width=True):
                    msg = f"طلبية: {cust}\n" + "\n".join([f"- {i}: {q}" for i, q in st.session_state.cart.items()])
                    url_wa = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold;">فتح واتساب الآن</button></a>', unsafe_allow_html=True)
                
                if st.button("🗑️ تفريغ السلة"):
                    st.session_state.cart = {}
                    st.rerun()

    # --- صفحة التفاصيل (الترتيب الهرمي) ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="header-box"><h2>قسم {cat}</h2></div>', unsafe_allow_html=True)
        
        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()

        cat_df = df[df['الالقسم'] == cat] if 'الالقسم' in df else df[df['القسم'] == cat]
        
        # الترتيب: 1. الوزن (العمود B)
        for w in cat_df['الوزن'].unique():
            st.markdown(f'<div class="weight-title">⚖️ {w}</div>', unsafe_allow_html=True)
            
            w_df = cat_df[cat_df['الوزن'] == w]
            # الترتيب: 2. الفئة (العمود C)
            for f in w_df['الفئة'].unique():
                st.markdown(f'<div class="sub-cat">📍 {f}</div>', unsafe_allow_html=True)
                
                # الترتيب: 3. الأصناف (العمود D)
                items_df = w_df[w_df['الفئة'] == f]
                for _, row in items_df.iterrows():
                    c1, c2 = st.columns([3, 1])
                    with c1: st.markdown(f'<div class="item-card">{row["الاسم"]}</div>', unsafe_allow_html=True)
                    with c2:
                        kid = f"q_{row['العلمي']}_{row['الوزن']}"
                        cur = st.session_state.cart.get(f"{row['الاسم']} ({row['الوزن']})", "")
                        val = st.text_input("", value=cur, key=kid, label_visibility="collapsed")
                        if val: st.session_state.cart[f"{row['الاسم']} ({row['الوزن']})"] = val


