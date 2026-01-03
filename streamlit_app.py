import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# 2. الرابط المباشر لبيانات ورقة "طلبات"
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=طلبات"

@st.cache_data(ttl=1)
def load_data():
    try:
        # سحب البيانات وتسمية الأعمدة بناءً على ترتيب ملفك
        df = pd.read_csv(URL, header=None).dropna(how='all')
        df.columns = ['القسم', 'الوزن', 'الفئة', 'الاسم', 'العلمي']
        return df
    except:
        return None

df = load_data()

# 3. تصميم الواجهة (CSS) لتجنب السواد وضمان وضوح الألوان
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .header-box { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 12px; border-bottom: 4px solid #fca311; margin-bottom: 20px; }
    .weight-row { background-color: #fca311; color: #1E3A8A; padding: 8px; border-radius: 8px; font-weight: bold; margin-top: 20px; text-align: center; }
    .sub-cat-label { color: #fca311; font-weight: bold; margin-top: 15px; border-right: 4px solid #fca311; padding-right: 10px; }
    .item-card { background-color: #1c2333; padding: 12px; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 8px; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; }
    .stButton button { border-radius: 10px; height: 50px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 4. إدارة حالة التطبيق (السلة والصفحات)
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is not None:
    # --- الصفحة الرئيسية ---
    if st.session_state.page == 'home':
        st.markdown('<div class="header-box"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        # محرك البحث السريع (الذي ظهر في صورتك الناجحة)
        search = st.text_input("🔍 بحث مباشر (أرز، حمص...):", placeholder="اكتب اسم الصنف هنا...")
        
        if search:
            results = df[df['الاسم'].str.contains(search, na=False)]
            for _, r in results.iterrows():
                st.markdown(f'<div class="item-card">{r["الاسم"]} ({r["الوزن"]})</div>', unsafe_allow_html=True)
                q_key = f"search_{r['العلمي']}_{r['الوزن']}"
                q_val = st.text_input("الكمية", key=q_key, label_visibility="collapsed")
                if q_val: st.session_state.cart[f"{r['الاسم']} ({r['الوزن']})"] = q_val
        else:
            st.write("### 📂 اختيارات الأقسام:")
            for cat in df['القسم'].unique():
                if st.button(f"📦 {cat}"):
                    st.session_state.sel_cat = cat
                    st.session_state.page = 'details'
                    st.rerun()

        # --- منطقة المشاهدة وتثبيت الطلب ---
        if st.session_state.cart:
            st.markdown("---")
            with st.expander("🛒 مشاهدة الطلبية الحالية", expanded=True):
                for item, qty in list(st.session_state.cart.items()):
                    st.write(f"✅ {item}: **{qty}**")
                
                cust_name = st.text_input("👤 اسم المندوب / الزبون:")
                if st.button("🚀 تثبيت الطلب وإرسال واتساب", type="primary"):
                    if cust_name:
                        msg = f"طلبية من: {cust_name}\n" + "\n".join([f"- {i}: {q}" for i, q in st.session_state.cart.items()])
                        wa_url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">تأكيد وفتح واتساب ✅</button></a>', unsafe_allow_html=True)
                    else:
                        st.warning("يرجى كتابة اسم الزبون لتثبيت الطلب")
                
                if st.button("🗑️ تفريغ السلة"):
                    st.session_state.cart = {}
                    st.rerun()

    # --- صفحة التفاصيل (الترتيب الهرمي المطلوب) ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="header-box"><h2>قسم {cat}</h2></div>', unsafe_allow_html=True)
        
        if st.button("🔙 العودة للقائمة"):
            st.session_state.page = 'home'
            st.rerun()

        cat_df = df[df['القسم'] == cat]
        
        # الترتيب الهرمي: 1. الوزن (العمود B)
        for w in cat_df['الوزن'].unique():
            st.markdown(f'<div class="weight-row">⚖️ قياس {w}</div>', unsafe_allow_html=True)
            
            w_df = cat_df[cat_df['الوزن'] == w]
            # الترتيب الهرمي: 2. الفئة (العمود C)
            for f in w_df['الفئة'].unique():
                st.markdown(f'<div class="sub-cat-label">📍 {f}</div>', unsafe_allow_html=True)
                
                # الترتيب الهرمي: 3. الأصناف (العمود D)
                items = w_df[w_df['الفئة'] == f]
                for _, row in items.iterrows():
                    c1, c2 = st.columns([3, 1])
                    with c1: st.markdown(f'<div class="item-card">{row["الاسم"]}</div>', unsafe_allow_html=True)
                    with c2:
                        k_id = f"qty_{row['العلمي']}_{row['الوزن']}"
                        # الحفاظ على الكمية المكتوبة سابقاً
                        old_val = st.session_state.cart.get(f"{row['الاسم']} ({row['الوزن']})", "")
                        v = st.text_input("", value=old_val, key=k_id, label_visibility="collapsed", placeholder="0")
                        if v: st.session_state.cart[f"{row['الاسم']} ({row['الوزن']})"] = v
