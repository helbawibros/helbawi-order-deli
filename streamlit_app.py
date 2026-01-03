import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# الرابط الصحيح والمباشر من صورتك
DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRMNeseeCy7logkwged_RZRu83VH3KXOHBurgahfwyi_LjGfd2CmD9-Mt-tCAO4C3xT8LWOIZaTUrX/pub?gid=283264234&single=true&output=csv"

@st.cache_data(ttl=10) # تحديث سريع جداً كل 10 ثوانٍ
def load_database():
    try:
        # قراءة الملف مع التأكد من تجاهل الأسطر الفارغة
        df = pd.read_csv(DB_URL).dropna(how='all')
        # تسمية الأعمدة بناءً على ترتيبك (A, B, C, D, E)
        df.columns = ['main_cat', 'package', 'sub_title', 'display_name', 'scientific_name']
        return df
    except Exception as e:
        return None

df = load_database()

# 2. تصميم الواجهة
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .main-header { background-color: #1E3A8A; color: white; text-align: center; padding: 20px; border-radius: 10px; border-bottom: 5px solid #fca311; }
    .category-btn { margin-bottom: 10px; }
    .pack-header { background-color: #fca311; color: #1E3A8A; padding: 8px; border-radius: 5px; font-weight: bold; margin-top: 15px; text-align: right; }
    .sub-title { color: #fca311; font-size: 1.2rem; font-weight: bold; margin-top: 10px; text-align: right; border-right: 4px solid #fca311; padding-right: 10px; }
    .item-card { background-color: #1E3A8A; padding: 12px; border-radius: 8px; font-weight: bold; text-align: right; border: 1px solid #333; margin-bottom: 5px; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; font-size: 18px !important; text-align: center !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 50px; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.markdown('<div class="main-header"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    
    if df is not None:
        main_categories = df['main_cat'].unique()
        st.write("### 📂 اختر القسم:")
        for cat in main_categories:
            if st.button(cat, key=f"btn_{cat}"):
                st.session_state.selected_cat = cat
                st.session_state.page = 'details'
                st.rerun()
    else:
        st.error("⚠️ فشل في تحميل البيانات. تأكد من أن الإنترنت يعمل وأن الرابط صحيح.")

    if st.session_state.cart:
        st.divider()
        with st.expander("🛒 مراجعة السلة", expanded=True):
            for sci, qty in list(st.session_state.cart.items()):
                st.write(f"✅ {sci} : {qty}")
            cust = st.text_input("اسم الزبون:")
            if st.button("🚀 إرسال الطلبية"):
                msg = f"طلبية: *{cust}*\n" + "\n".join([f"{k}: {v}" for k, v in st.session_state.cart.items()])
                url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank">اضغط هنا للتأكيد</a>', unsafe_allow_html=True)

# --- صفحة التفاصيل ---
elif st.session_state.page == 'details':
    cat = st.session_state.selected_cat
    st.markdown(f'<div class="main-header"><h2>قسم {cat}</h2></div>', unsafe_allow_html=True)
    
    cat_df = df[df['main_cat'] == cat]
    for pack in cat_df['package'].unique():
        st.markdown(f'<div class="pack-header">تعبئة {pack}</div>', unsafe_allow_html=True)
        pack_df = cat_df[cat_df['package'] == pack]
        
        for sub in pack_df['sub_title'].unique():
            st.markdown(f'<div class="sub-title">{sub}</div>', unsafe_allow_html=True)
            sub_df = pack_df[pack_df['sub_title'] == sub]
            
            for _, row in sub_df.iterrows():
                c1, c2 = st.columns([3, 1])
                with c1: st.markdown(f'<div class="item-card">{row["display_name"]}</div>', unsafe_allow_html=True)
                with c2:
                    # مفتاح فريد لكل مدخل لمنع خطأ Duplicate Key
                    key = f"in_{row['scientific_name']}_{row['package']}"
                    current_val = st.session_state.cart.get(row['scientific_name'], "")
                    val = st.text_input("", value=current_val, key=key, label_visibility="collapsed")
                    if val and val.isdigit() and int(val) > 0:
                        st.session_state.cart[row['scientific_name']] = val
                    elif val == "0" and row['scientific_name'] in st.session_state.cart:
                        del st.session_state.cart[row['scientific_name']]

    if st.button("🔙 العودة"):
        st.session_state.page = 'home'
        st.rerun()
