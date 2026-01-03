import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="طلبيات حلباوي", layout="wide")

# 2. الرابط المباشر (تأكد أن اسم الورقة في الملف هو "طلبات")
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
SHEET_NAME = "طلبات"
DIRECT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"

@st.cache_data(ttl=1)
def load_data():
    try:
        # قراءة البيانات وتسمية الأعمدة بناءً على ترتيب ملفك
        df = pd.read_csv(DIRECT_URL, header=None).dropna(how='all')
        df = df.iloc[:, :5]
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except Exception as e:
        return None

df = load_data()

# 3. تصميم الواجهة (الألوان والأسهم)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 10px; border-bottom: 5px solid #fca311; margin-bottom: 20px; }
    /* تنسيق كبسة السهم (Expander) */
    .stExpander { background-color: #1c2333 !important; border: 1px solid #fca311 !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    .item-card { background-color: #262730; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-right: 4px solid #fca311; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; width: 100%; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is not None:
    # --- الصفحة الرئيسية (الأقسام الكبيرة) ---
    if st.session_state.page == 'home':
        st.markdown('<div class="header"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        # عرض الأقسام (A) كأزرار
        for c in df['cat'].unique():
            if st.button(f"📦 قسم {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        # عرض ملخص السلة وتثبيت الطلب
        if st.session_state.cart:
            st.divider()
            with st.expander("🛒 عرض الأصناف المختارة وتثبيت الطلب"):
                for k, v in list(st.session_state.cart.items()):
                    st.write(f"🔹 {k}: **{v}**")
                
                cust = st.text_input("👤 اسم المندوب / الزبون:")
                if st.button("🚀 إرسال الطلبية كاملة"):
                    if cust:
                        msg = f"طلبية: {cust}\n" + "\n".join([f"- {item}: {qty}" for item, qty in st.session_state.cart.items()])
                        url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold;">فتح واتساب لإرسال الطلب ✅</button></a>', unsafe_allow_html=True)
                    else:
                        st.warning("يرجى إدخال الاسم أولاً")

    # --- صفحة التفاصيل (نظام الأسهم المنسدلة) ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        if st.button("🔙 عودة للأقسام"):
            st.session_state.page = 'home'
            st.rerun()

        filtered = df[df['cat'] == cat]
        
        # إنشاء سهم (Expander) لكل وزن موجود في العمود B
        for weight in filtered['pack'].unique():
            with st.expander(f"➡️ {weight}"):
                w_df = filtered[filtered['pack'] == weight]
                
                # عرض الأصناف داخل السهم
                for _, row in w_df.iterrows():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        # عرض الفئة (C) واسم الصنف (D)
                        st.markdown(f'<div class="item-card"><b>{row["sub"]}</b> - {row["name"]}</div>', unsafe_allow_html=True)
                    with c2:
                        key = f"q_{row['name']}_{row['pack']}"
                        curr = st.session_state.cart.get(f"{row['name']} ({row['pack']})", "")
                        val = st.text_input("", value=curr, key=key, label_visibility="collapsed", placeholder="0")
                        
                        if val and val.isdigit() and int(val) > 0:
                            st.session_state.cart[f"{row['name']} ({row['pack']})"] = val
                        elif val == "0" and f"{row['name']} ({row['pack']})" in st.session_state.cart:
                            del st.session_state.cart[f"{row['name']} ({row['pack']})"]
