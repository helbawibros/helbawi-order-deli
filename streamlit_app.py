import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# الرابط المباشر من ملفك (تأكد من نسخه كاملاً)
DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRMNeseeCy7logkwged_RZRu83VH3KXOHBurgahfwyi_LjGfd2CmD9-Mt-tCAO4C3xT8LWOIZaTUrX/pub?gid=283264234&single=true&output=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        # قراءة البيانات مباشرة بدون عناوين (header=None) لتجنب ضياع السطر الأول
        df = pd.read_csv(DB_URL, header=None).dropna(how='all')
        # تعيين أسماء الأعمدة برمجياً لتطابق ترتيبك
        df.columns = ['main_cat', 'pack', 'sub_title', 'display', 'scientific']
        return df
    except:
        return None

df = load_data()

# تصميم بسيط وسريع للهاتف
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 10px; border-bottom: 4px solid #fca311; }
    .item-card { background-color: #1c2333; padding: 12px; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 8px; text-align: right; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; height: 40px !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; width: 100%; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is None:
    st.warning("⚠️ جوجل يحتاج دقيقة لتفعيل الرابط. يرجى تحديث الصفحة (Refresh) بعد قليل.")
else:
    if st.session_state.page == 'home':
        st.markdown('<div class="header"><h1>طلبيات حلباوي</h1></div>', unsafe_allow_html=True)
        
        # استخراج الأقسام من العمود A
        categories = df['main_cat'].unique()
        st.write("### اختر القسم:")
        for cat in categories:
            if st.button(f"📦 {cat}"):
                st.session_state.selected_cat = cat
                st.session_state.page = 'details'
                st.rerun()
                
        if st.session_state.cart:
            st.divider()
            customer = st.text_input("👤 اسم الزبون:")
            if st.button("✅ إرسال الطلبية"):
                order_list = [f"{sci}: {qty}" for sci, qty in st.session_state.cart.items()]
                msg = f"طلبية: {customer}\n" + "\n".join(order_list)
                whatsapp_url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold;">تأكيد عبر واتساب</button></a>', unsafe_allow_html=True)

    elif st.session_state.page == 'details':
        cat = st.session_state.selected_cat
        st.markdown(f'<div class="header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        filtered = df[df['main_cat'] == cat]
        
        # عرض حسب العنوان الفرعي (العمود C)
        for sub in filtered['sub_title'].unique():
            st.markdown(f"🔹 **{sub}**")
            sub_df = filtered[filtered['sub_title'] == sub]
            
            for _, row in sub_df.iterrows():
                c1, c2 = st.columns([3, 1])
                with c1:
                    # عرض اسم المنتج (العمود D) والتعبئة (العمود B)
                    st.markdown(f'<div class="item-card">{row["display"]} - {row["pack"]}</div>', unsafe_allow_html=True)
                with c2:
                    # استخدام الاسم العلمي (العمود E) كمفتاح
                    key = f"q_{row['scientific']}_{row['pack']}"
                    current = st.session_state.cart.get(row['scientific'], "")
                    val = st.text_input("", value=current, key=key, label_visibility="collapsed")
                    if val and val.isdigit() and int(val) > 0:
                        st.session_state.cart[row['scientific']] = val
                    elif val == "0" and row['scientific'] in st.session_state.cart:
                        del st.session_state.cart[row['scientific']]

        if st.button("🔙 عودة"):
            st.session_state.page = 'home'
            st.rerun()

