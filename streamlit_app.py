import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة والربط بملف الأكسل (الرابط المستخرج من صورتك)
st.set_page_config(page_title="حلباوي إخوان - نظام الطلبيات", layout="wide")

# الرابط الذي حصلت عليه من "Publish to web" في صورتك الأخيرة
DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRMNeseeCy7logkwged_RZRu83VH3KXOHBurgahfwyi_LjGfd2CmD9-Mt-tCAO4C3xT8LWOIZaTUrX/pub?gid=283264234&single=true&output=csv"

def load_database():
    try:
        # قراءة البيانات مع تحديد الأسماء بناءً على ترتيب أعمدتك (A, B, C, D, E)
        df = pd.read_csv(DB_URL)
        df.columns = ['main_cat', 'package', 'sub_title', 'display_name', 'scientific_name']
        return df
    except Exception as e:
        st.error(f"⚠️ خطأ في الاتصال: تأكد من أن الملف منشور (Publish to Web) بصيغة CSV")
        return None

df = load_database()

# 2. تصميم الواجهة (الألوان والهوية البصرية)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .main-header { background-color: #1E3A8A; color: white; text-align: center; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-bottom: 5px solid #fca311; }
    .pack-header { background-color: #fca311; color: #1E3A8A; padding: 8px; border-radius: 5px; font-weight: bold; margin-top: 15px; text-align: right; }
    .sub-title { color: #fca311; font-size: 1.2rem; font-weight: bold; margin-top: 10px; text-align: right; border-right: 4px solid #fca311; padding-right: 10px; }
    .item-card { background-color: #1E3A8A; color: white; padding: 12px; border-radius: 8px; font-weight: bold; text-align: right; border: 1px solid #333; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; font-size: 18px !important; text-align: center !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 55px; font-size: 1.1rem; }
    .footer-note { color: #888; text-align: center; font-size: 0.8rem; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة الجلسة والطلبات
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية (الأقسام الكبيرة) ---
if st.session_state.page == 'home':
    st.markdown('<div class="main-header"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
    
    if df is not None:
        # استخراج الأقسام من العمود A
        categories = df['main_cat'].unique()
        st.write("### 📂 اختر قسم المنتجات:")
        
        # توزيع الأقسام على أزرار
        for cat in categories:
            if st.button(f"📦 {cat}", use_container_width=True):
                st.session_state.selected_cat = cat
                st.session_state.page = 'details'
                st.rerun()

    # قسم المراجعة والإرسال
    if st.session_state.cart:
        st.markdown("---")
        with st.expander("🛒 مراجعة الطلبية الحالية", expanded=True):
            for sci, qty in list(st.session_state.cart.items()):
                st.write(f"✅ **{sci}** | الكمية: `{qty}`")
            
            customer = st.text_input("👤 اسم الزبون / المندوب:")
            if st.button("🚀 إرسال الطلبية عبر واتساب"):
                if not customer:
                    st.warning("الرجاء إدخال اسم الزبون")
                else:
                    text = f"طلبية: *{customer}*\n" + "="*15 + "\n"
                    for s, q in st.session_state.cart.items():
                        text += f"{s} : {q}\n"
                    
                    link = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(text)}"
                    st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">تأكيد وفتح واتساب ✅</button></a>', unsafe_allow_html=True)
            
            if st.button("🗑️ مسح السلة"):
                st.session_state.cart = {}
                st.rerun()

# --- صفحة المنتجات التفصيلية ---
elif st.session_state.page == 'details':
    cat_name = st.session_state.selected_cat
    st.markdown(f'<div class="main-header"><h2>قسم {cat_name}</h2></div>', unsafe_allow_html=True)
    
    # تصفية البيانات حسب القسم المختار (العمود A)
    filtered_df = df[df['main_cat'] == cat_name]
    
    # تقسيم حسب التعبئة (العمود B)
    for pack in filtered_df['package'].unique():
        st.markdown(f'<div class="pack-header">تعبئة: {pack}</div>', unsafe_allow_html=True)
        pack_df = filtered_df[filtered_df['package'] == pack]
        
        # تقسيم حسب العنوان الفرعي (العمود C)
        for sub in pack_df['sub_title'].unique():
            st.markdown(f'<div class="sub-title">{sub}</div>', unsafe_allow_html=True)
            sub_df = pack_df[pack_df['sub_title'] == sub]
            
            for _, row in sub_df.iterrows():
                col_name, col_input = st.columns([3, 1])
                with col_name:
                    st.markdown(f'<div class="item-card">{row["display_name"]}</div>', unsafe_allow_html=True)
                with col_input:
                    # المفتاح البرمجي هو الاسم العلمي لضمان عدم التكرار (العمود E)
                    current_qty = st.session_state.cart.get(row['scientific_name'], "")
                    val = st.text_input("", value=current_qty, key=f"q_{row['scientific_name']}", label_visibility="collapsed", placeholder="0")
                    
                    if val:
                        # تحويل الأرقام العربية إلى إنجليزية للتخزين
                        clean_v = val.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
                        if clean_v.isdigit() and int(clean_v) > 0:
                            st.session_state.cart[row['scientific_name']] = clean_v
                        elif clean_v == "0" and row['scientific_name'] in st.session_state.cart:
                            del st.session_state.cart[row['scientific_name']]

    if st.button("🔙 العودة للقائمة الرئيسية"):
        st.session_state.page = 'home'
        st.rerun()

st.markdown('<div class="footer-note">نظام إدارة الطلبيات - حلباوي إخوان © 2024</div>', unsafe_allow_html=True)
