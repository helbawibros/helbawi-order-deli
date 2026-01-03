import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة والربط بملف الأكسل (الرابط من صورتك)
st.set_page_config(page_title="حلباوي إخوان - الطلبيات", layout="wide")

# الرابط المستخرج من صورتك الأخيرة (CSV)
DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRMNeseeCy7logkwged_RZRu83VH3KXOHBurgahfwyi_LjGfd2CmD9-Mt-tCAO4C3xT8LWOIZaTUrX/pub?gid=283264234&single=true&output=csv"

@st.cache_data(ttl=60) # تحديث البيانات كل دقيقة
def load_database():
    try:
        # قراءة البيانات بناءً على ترتيب أعمدتك (A, B, C, D, E)
        df = pd.read_csv(DB_URL)
        df.columns = ['main_cat', 'package', 'sub_title', 'display_name', 'scientific_name']
        return df
    except:
        return None

df = load_database()

# 2. تصميم الواجهة (الألوان والخطوط)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .main-header { background-color: #1E3A8A; color: white; text-align: center; padding: 25px; border-radius: 12px; margin-bottom: 25px; border-bottom: 5px solid #fca311; }
    .pack-header { background-color: #fca311; color: #1E3A8A; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 20px; text-align: right; }
    .sub-title { color: #fca311; font-size: 1.3rem; font-weight: bold; margin-top: 15px; text-align: right; border-right: 5px solid #fca311; padding-right: 12px; }
    .item-card { background-color: #1c2333; color: white; padding: 15px; border-radius: 10px; font-weight: bold; text-align: right; border: 1px solid #2d3748; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; font-size: 20px !important; text-align: center !important; height: 45px !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 60px; font-size: 1.2rem; border-radius: 12px; }
    .footer-note { color: #718096; text-align: center; font-size: 0.9rem; margin-top: 60px; border-top: 1px solid #2d3748; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة الجلسة
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.markdown('<div class="main-header"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    
    if df is not None:
        # استخراج الأقسام من العمود A (حبوب، بهارات...)
        categories = df['main_cat'].unique()
        st.write("### 📂 اختر قسم المنتجات:")
        
        for cat in categories:
            if st.button(f"📦 {cat}", use_container_width=True):
                st.session_state.selected_cat = cat
                st.session_state.page = 'details'
                st.rerun()
    else:
        st.error("⚠️ خطأ في الاتصال بالملف. تأكد من إعدادات 'Publish to web' في الأكسل.")

    # مراجعة السلة
    if st.session_state.cart:
        st.markdown("---")
        with st.expander("🛒 مراجعة السلة الحالية", expanded=True):
            for sci, qty in list(st.session_state.cart.items()):
                st.write(f"✅ **{sci}** — الكمية: `{qty}`")
            
            customer = st.text_input("👤 اسم الزبون / المندوب:", key="cust_name")
            if st.button("🚀 إرسال الطلبية كاملة"):
                if not customer:
                    st.warning("الرجاء كتابة اسم الزبون!")
                else:
                    text = f"طلبية: *{customer}*\n" + "="*15 + "\n"
                    for s, q in st.session_state.cart.items():
                        text += f"{s} : {q}\n"
                    
                    link = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(text)}"
                    st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">تأكيد وفتح واتساب ✅</button></a>', unsafe_allow_html=True)
            
            if st.button("🗑️ تفريغ السلة"):
                st.session_state.cart = {}
                st.rerun()

# --- صفحة المنتجات التفصيلية ---
elif st.session_state.page == 'details':
    cat_name = st.session_state.selected_cat
    st.markdown(f'<div class="main-header"><h2>قسم {cat_name}</h2></div>', unsafe_allow_html=True)
    
    # تصفية المنتجات حسب القسم
    cat_df = df[df['main_cat'] == cat_name]
    
    # التنظيم حسب التعبئة (العمود B)
    for pack in cat_df['package'].unique():
        st.markdown(f'<div class="pack-header">تعبئة: {pack}</div>', unsafe_allow_html=True)
        pack_df = cat_df[cat_df['package'] == pack]
        
        # التنظيم حسب العنوان الفرعي (العمود C)
        for sub in pack_df['sub_title'].unique():
            st.markdown(f'<div class="sub-title">{sub}</div>', unsafe_allow_html=True)
            sub_df = pack_df[pack_df['sub_title'] == sub]
            
            for _, row in sub_df.iterrows():
                col_name, col_input = st.columns([3, 1])
                with col_name:
                    st.markdown(f'<div class="item-card">{row["display_name"]}</div>', unsafe_allow_html=True)
                with col_input:
                    # نستخدم الاسم العلمي كـ Key (العمود E)
                    current_qty = st.session_state.cart.get(row['scientific_name'], "")
                    val = st.text_input("", value=current_qty, key=f"q_{row['scientific_name']}", label_visibility="collapsed", placeholder="0")
                    
                    if val:
                        clean_v = val.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
                        if clean_v.isdigit() and int(clean_v) > 0:
                            st.session_state.cart[row['scientific_name']] = clean_v
                        elif clean_v == "0" and row['scientific_name'] in st.session_state.cart:
                            del st.session_state.cart[row['scientific_name']]

    if st.button("🔙 العودة للقائمة وحفظ الطلب"):
        st.session_state.page = 'home'
        st.rerun()

st.markdown('<div class="footer-note">نظام إدارة الطلبيات - حلباوي إخوان © 2026</div>', unsafe_allow_html=True)
