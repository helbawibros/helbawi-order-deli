import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# الرابط المباشر من صورتك
DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRMNeseeCy7logkwged_RZRu83VH3KXOHBurgahfwyi_LjGfd2CmD9-Mt-tCAO4C3xT8LWOIZaTUrX/pub?gid=283264234&single=true&output=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        # قراءة البيانات بدون اعتبار السطر الأول كعنوان
        df = pd.read_csv(DB_URL, header=None)
        # تسمية الأعمدة برمجياً بناءً على صورك
        df.columns = ['A', 'B', 'C', 'D', 'E']
        return df
    except:
        return None

df = load_data()

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .header { background-color: #1E3A8A; text-align: center; padding: 20px; border-radius: 10px; border-bottom: 5px solid #fca311; margin-bottom: 20px; }
    .item-box { background-color: #1c2333; padding: 15px; border-radius: 10px; border: 1px solid #2d3748; margin-bottom: 10px; text-align: right; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is None:
    st.error("⚠️ الرابط لا يزال غير جاهز من طرف جوجل. يرجى الانتظار دقيقتين أو التأكد من اختيار 'Comma-separated values (.csv)' عند النشر.")
else:
    if st.session_state.page == 'home':
        st.markdown('<div class="header"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        # عرض الأقسام من العمود A
        cats = df['A'].unique()
        for c in cats:
            if st.button(f"📦 {c}", use_container_width=True):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
                
        if st.session_state.cart:
            st.divider()
            cust = st.text_input("👤 اسم الزبون:")
            if st.button("🚀 إرسال عبر واتساب", use_container_width=True):
                msg = f"طلبية: {cust}\n" + "\n".join([f"{k}: {v}" for k, v in st.session_state.cart.items()])
                url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank">اضغط هنا لفتح واتساب</a>', unsafe_allow_html=True)

    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="header"><h2>قسم {cat}</h2></div>', unsafe_allow_html=True)
        
        filtered = df[df['A'] == cat]
        
        # التنظيم حسب العمود C (العناوين الفرعية)
        for sub in filtered['C'].unique():
            st.warning(f"📍 {sub}")
            sub_df = filtered[filtered['C'] == sub]
            
            for _, row in sub_df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f'<div class="item-box">{row["D"]} ({row["B"]})</div>', unsafe_allow_html=True)
                with col2:
                    # مفتاح فريد يجمع الاسم والتعبئة لمنع خطأ التكرار
                    key = f"{row['E']}_{row['B']}"
                    val = st.text_input("", key=key, label_visibility="collapsed", placeholder="0")
                    if val and val.isdigit():
                        st.session_state.cart[row['E']] = val

        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()
