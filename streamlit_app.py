import streamlit as st
import pandas as pd
import urllib.parse

# الرابط المباشر للملف (Live Data)
# ملاحظة: تم تعديل الرابط برمجياً ليقوم بالتصدير المباشر
SHEET_ID = "1Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
GID = "283264234"
DIRECT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

st.set_page_config(page_title="حلباوي إخوان", layout="wide")

@st.cache_data(ttl=1) # تحديث فوري
def load_data():
    try:
        # قراءة البيانات مع تجاهل الترويسة لأن ملفك يبدأ بالبيانات فوراً
        df = pd.read_csv(DIRECT_URL, header=None).dropna(how='all')
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except:
        return None

df = load_data()

# تصميم مخصص للهواتف لسهولة الاستخدام
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 10px; border-bottom: 4px solid #fca311; margin-bottom: 15px; }
    .item-card { background-color: #1c2333; padding: 12px; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 8px; text-align: right; font-size: 1.1rem; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; font-size: 1.2rem !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; width: 100%; height: 50px; border-radius: 10px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is None or df.empty:
    st.error("⚠️ يرجى التأكد من تفعيل 'Anyone with the link' في إعدادات Manage Access.")
else:
    if st.session_state.page == 'home':
        st.markdown('<div class="header"><h1>طلبيات حلباوي</h1></div>', unsafe_allow_html=True)
        # عرض الأقسام الرئيسية (حبوب، بهارات) من العمود الأول
        for c in df['cat'].unique():
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
                st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">تأكيد وفتح واتساب</button></a>', unsafe_allow_html=True)

    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        filtered = df[df['cat'] == cat]
        for sub in filtered['sub'].unique():
            st.markdown(f"🔹 **{sub}**")
            sub_df = filtered[filtered['sub'] == sub]
            for _, row in sub_df.iterrows():
                c1, c2 = st.columns([3, 1])
                with c1:
                    # عرض اسم الصنف من العمود الرابع
                    st.markdown(f'<div class="item-card">{row["name"]}</div>', unsafe_allow_html=True)
                with c2:
                    # مفتاح فريد لمنع خطأ Duplicate Key الذي ظهر في صورتك السابقة
                    key = f"q_{row['sci']}_{row['pack']}"
                    val = st.text_input("", key=key, label_visibility="collapsed", placeholder="0")
                    if val and val.isdigit() and int(val) > 0:
                        st.session_state.cart[row['name']] = val

        if st.button("🔙 عودة للقائمة الرئيسية"):
            st.session_state.page = 'home'
            st.rerun()
