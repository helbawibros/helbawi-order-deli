import streamlit as st
import pandas as pd
import urllib.parse

# إعدادات الصفحة
st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# الرابط المباشر والقوي الذي نجح في الاتصال
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
DIRECT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=طلبات"

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(DIRECT_URL, header=None).dropna(how='all')
        df.columns = ['القسم', 'الوزن', 'الفئة', 'الاسم', 'العلمي']
        return df
    except:
        return None

df = load_data()

# تصميم الواجهة (ألوان الهوية والترتيب)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .main-header { background-color: #1E3A8A; text-align: center; padding: 20px; border-radius: 15px; border-bottom: 5px solid #fca311; margin-bottom: 20px; }
    .sub-title { background-color: #fca311; color: #1E3A8A; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 20px; text-align: center; }
    .item-box { background-color: #1c2333; padding: 15px; border-radius: 10px; border: 1px solid #2d3748; margin-bottom: 10px; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; font-size: 1.2rem !important; }
    .stButton button { border-radius: 10px; height: 55px; font-weight: bold; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is not None:
    # --- الصفحة الرئيسية (الأقسام الكبيرة) ---
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        # البحث السريع
        search = st.text_input("🔍 ابحث عن صنف معين مباشرة:", placeholder="مثلاً: ارز مصري...")
        
        if search:
            results = df[df['الاسم'].str.contains(search, na=False)]
            for _, r in results.iterrows():
                st.markdown(f'<div class="item-box">{r["الاسم"]} ({r["الوزن"]})</div>', unsafe_allow_html=True)
                qty = st.text_input("الكمية", key=f"s_{r['العلمي']}", label_visibility="collapsed")
                if qty: st.session_state.cart[f"{r['الاسم']} ({r['الوزن']})"] = qty
        else:
            # عرض الأقسام (A)
            st.write("### 📂 الأقسام الرئيسية:")
            for cat in df['القسم'].unique():
                if st.button(f"📦 {cat}", use_container_width=True):
                    st.session_state.sel_cat = cat
                    st.session_state.page = 'details'
                    st.rerun()

        # زر المشاهدة والتثبيت (يظهر فقط إذا السلة ممتلئة)
        if st.session_state.cart:
            st.markdown("---")
            with st.expander("🛒 عرض الطلبية الحالية", expanded=True):
                for item, q in st.session_state.cart.items():
                    st.write(f"🔹 {item}: **{q}**")
                
                name = st.text_input("👤 اسم الزبون:")
                if st.button("🚀 تثبيت وإرسال الطلب (واتساب)", type="primary", use_container_width=True):
                    msg = f"طلبية من: {name}\n" + "\n".join([f"- {k}: {v}" for k, v in st.session_state.cart.items()])
                    url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">تأكيد الإرسال ✅</button></a>', unsafe_allow_html=True)

    # --- صفحة المنتجات (الترتيب الهرمي) ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="main-header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        filtered = df[df['القسم'] == cat]
        
        # الترتيب حسب الوزن (B) ثم الفئة (C)
        for weight in filtered['الوزن'].unique():
            st.markdown(f'<div class="sub-title">⚖️ قياس: {weight}</div>', unsafe_allow_html=True)
            
            weight_df = filtered[filtered['الوزن'] == weight]
            for sub in weight_df['الفئة'].unique():
                st.write(f"📍 **{sub}**")
                sub_df = weight_df[weight_df['الفئة'] == sub]
                
                for _, row in sub_df.iterrows():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f'<div class="item-box">{row["الاسم"]}</div>', unsafe_allow_html=True)
                    with c2:
                        k = f"in_{row['العلمي']}_{row['الوزن']}"
                        curr = st.session_state.cart.get(f"{row['الاسم']} ({row['الوزن']})", "")
                        val = st.text_input("", value=curr, key=k, label_visibility="collapsed")
                        if val: st.session_state.cart[f"{row['الاسم']} ({row['الوزن']})"] = val

        if st.button("🔙 عودة للقائمة"):
            st.session_state.page = 'home'
            st.rerun()

