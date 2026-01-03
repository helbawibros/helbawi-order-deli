import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة والربط بـ Google Sheets
# استبدل هذا الرابط برابط ملفك مع التأكد أنه متاح لمن يملك الرابط (Anyone with link)
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=YOUR_GID"

def load_data():
    # قراءة الداتا من الشيت الجديد "طلبات"
    df = pd.read_csv(SHEET_URL)
    # تنظيف الأسماء من أي مسافات زائدة
    df.columns = ['main', 'pack', 'sub', 'display', 'scientific']
    return df

try:
    data_df = load_data()
except:
    st.error("يرجى التأكد من رابط ملف الأكسل وصلاحيات الوصول")
    st.stop()

# 2. تصميم الواجهة (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .category-header { background-color: #e9ecef; color: #1E3A8A; padding: 10px; border-radius: 5px; font-weight: bold; margin-top: 20px; text-align: right; }
    .item-box { color: white; background-color: #1E3A8A; padding: 10px; border-radius: 8px; text-align: right; width: 100%; font-weight: bold; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; font-size: 18px !important; }
    .header-box { background-color: #1E3A8A; color: white; text-align: center; padding: 20px; border-radius: 10px; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة الحالة
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

# --- الصفحة الرئيسية ---
if st.session_state.page == 'home':
    st.markdown('<div class="header-box"><h1>نظام طلبيات حلباوي</h1></div>', unsafe_allow_html=True)
    
    # استخراج الأقناف الرئيسية من العمود A
    main_categories = data_df['main'].unique()
    
    st.write("### اختر القسم:")
    cols = st.columns(len(main_categories))
    for i, cat in enumerate(main_categories):
        if cols[i].button(cat, use_container_width=True):
            st.session_state.selected_cat = cat
            st.session_state.page = 'details'
            st.rerun()

    # مراجعة وإرسال
    if st.session_state.cart:
        st.divider()
        st.write("### 📋 مراجعة الطلبية:")
        for sci_name, qty in st.session_state.cart.items():
            st.write(f"✅ {sci_name} | الكمية: {qty}")
        
        customer = st.text_input("اسم الزبون:")
        if st.button("🚀 إرسال عبر واتساب"):
            msg = f"طلبية: {customer}\n" + "\n".join([f"{k}: {v}" for k, v in st.session_state.cart.items()])
            link = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link}" target="_blank">اضغط هنا للتأكيد</a>', unsafe_allow_html=True)

# --- صفحة التفاصيل (تبنى ديناميكياً) ---
elif st.session_state.page == 'details':
    cat = st.session_state.selected_cat
    st.markdown(f'<div class="header-box"><h2>قسم {cat}</h2></div>', unsafe_allow_html=True)
    
    # فلترة البيانات حسب القسم المختار
    filtered_df = data_df[data_df['main'] == cat]
    
    # تقسيم حسب التعبئة (العمود B)
    for pack in filtered_df['pack'].unique():
        st.markdown(f'<div class="category-header">📦 تعبئة {pack}</div>', unsafe_allow_html=True)
        pack_df = filtered_df[filtered_df['pack'] == pack]
        
        # تقسيم حسب العنوان الفرعي (العمود C)
        for sub in pack_df['sub'].unique():
            st.write(f"🔹 **{sub}**")
            sub_df = pack_df[pack_df['sub'] == sub]
            
            for _, row in sub_df.iterrows():
                col_txt, col_in = st.columns([3, 1])
                with col_txt: st.markdown(f'<div class="item-box">{row["display"]}</div>', unsafe_allow_html=True)
                with col_in:
                    # المفتاح هو الاسم العلمي (العمود E) لضمان الربط مع الفواتير
                    q = st.text_input("", key=f"in_{row['scientific']}", label_visibility="collapsed", placeholder="0")
                    if q and q.isdigit() and int(q) > 0:
                        st.session_state.cart[row['scientific']] = q
    
    if st.button("🔙 عودة للمراجعة"):
        st.session_state.page = 'home'
        st.rerun()
