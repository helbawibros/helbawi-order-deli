import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام طلبيات حلباوي", layout="centered")

# 2. جلب البيانات من جوجل شيت
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
SHEET_NAME = "طلبات"
DIRECT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_csv(DIRECT_URL, header=None).dropna(how='all')
        df = df.iloc[:, :5]
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except:
        return None

df = load_data()

# 3. التنسيق (الأزرار العريضة والمحاذاة لليمين)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    [data-testid="stSidebar"] { display: none; }
    
    /* الخانة الزرقاء العلويّة */
    .main-header { 
        background-color: #1E3A8A; 
        text-align: center; 
        padding: 35px 10px; 
        border-radius: 15px; 
        border-bottom: 8px solid #fca311; 
        margin-bottom: 25px; 
    }
    .main-header h1 { margin: 0; font-size: 35px !important; color: white; font-weight: 900; }
    .main-header p { margin: 10px 0 0 0; font-size: 22px; color: #fca311; font-weight: bold; }

    /* محاذاة النصوص لليمين */
    .info-box {
        background-color: #1c2333;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d3748;
        margin-bottom: 20px;
        font-size: 18px;
        text-align: right;
    }
    
    .sub-category-header { 
        background-color: #2d3748; color: #fca311; padding: 12px; 
        border-radius: 5px; font-weight: bold; margin-top: 20px; 
        text-align: right; border-right: 8px solid #fca311; 
        font-size: 20px;
    }
    
    .item-label { 
        background-color: #1E3A8A; color: white; padding: 15px; 
        border-radius: 8px; font-weight: bold; text-align: right; 
        margin-bottom: 3px; font-size: 20px;
    }
    
    /* خانة إدخال الأرقام */
    input { 
        background-color: #ffffcc !important; color: black !important; 
        font-weight: bold !important; text-align: right !important;
        height: 60px !important; border-radius: 8px !important; 
        font-size: 22px !important;
    }
    
    /* فرض عرض الأزرار بالكامل */
    div.stButton > button {
        width: 100% !important;
        background-color: #fca311 !important;
        color: #1E3A8A !important;
        font-weight: 900 !important;
        height: 75px !important;
        font-size: 22px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        border: none !important;
    }

    /* زر الواتساب الأخضر */
    .wa-link {
        text-decoration: none;
    }
    .wa-button {
        background-color: #25d366;
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        display: block;
        width: 100%;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# إدارة الحالة
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cust_name' not in st.session_state: st.session_state.cust_name = ""

now = datetime.now().strftime("%Y-%m-%d | %H:%M")

if df is not None:
    # --- الصفحة الرئيسية ---
    if st.session_state.page == 'home':
        st.markdown('''
            <div class="main-header">
                <h1>طلبيات المندوبين</h1>
                <p>شركة حلباوي إخوان</p>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f'<div class="info-box">🗓️ الوقت: {now} <br> 👤 المندوب: {st.session_state.cust_name if st.session_state.cust_name else "---"}</div>', unsafe_allow_html=True)

        st.markdown("<p style='text-align:right; font-weight:bold;'>👤 اسم المندوب / الزبون:</p>", unsafe_allow_html=True)
        st.session_state.cust_name = st.text_input("name_input", value=st.session_state.cust_name, label_visibility="collapsed")
        
        st.write("### 📂 الأقسام:")
        for c in df['cat'].unique():
            if st.button(f"📦 قسم {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        if st.session_state.cart:
            st.divider()
            if st.button("🛒 مراجعة وتثبيت الطلبية"):
                st.session_state.page = 'review'
                st.rerun()

    # --- صفحة التفاصيل ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="main-header"><h1>{cat}</h1><p>شركة حلباوي إخوان</p></div>', unsafe_allow_html=True)
        
        if st.button("🔙 العودة للقائمة"):
            st.session_state.page = 'home'
            st.rerun()

        cat_df = df[df['cat'] == cat]
        for weight in cat_df['pack'].unique():
            with st.expander(f"🔽 {weight}", expanded=True):
                w_df = cat_df[cat_df['pack'] == weight]
                for sub in w_df['sub'].unique():
                    st.markdown(f'<div class="sub-category-header">{sub}</div>', unsafe_allow_html=True)
                    for _, row in w_df[w_df['sub'] == sub].iterrows():
                        st.markdown(f'<div class="item-label">{row["name"]}</div>', unsafe_allow_html=True)
                        key = f"q_{row['name']}_{row['pack']}"
                        curr = st.session_state.cart.get(key, {}).get('qty', "")
                        val = st.text_input("العدد", value=curr, key=key+"_v", label_visibility="collapsed")
                        if val:
                            st.session_state.cart[key] = {'name': row['name'], 'qty': val}
                        elif val == "" and key in st.session_state.cart:
                            del st.session_state.cart[key]
        
        if st.button("✅ تثبيت ومراجعة"):
            st.session_state.page = 'review'
            st.rerun()

    # --- صفحة المراجعة النهائية ---
    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>مراجعة وتثبيت</h1><p>حلباوي إخوان</p></div>', unsafe_allow_html=True)
        
        if not st.session_state.cart:
            st.warning("السلة فارغة")
            if st.button("🏠 العودة"):
                st.session_state.page = 'home'
                st.rerun()
        else:
            st.markdown(f"<div class='info-box'>👤 المندوب: {st.session_state.cust_name} <br> ⏰ التوقيت: {now}</div>", unsafe_allow_html=True)
            
            items_list = []
            for k, v in st.session_state.cart.items():
                st.markdown(f"<p style='text-align:right; font-size:18px;'>✅ {v['name']} : <b>{v['qty']}</b></p>", unsafe_allow_html=True)
                items_list.append(f"{v['name']}: {v['qty']}")
            
            st.divider()
            st.write("### ➕ إضافة أصناف أخرى:")
            for c in df['cat'].unique():
                if st.button(f"العودة لـ {c}"):
                    st.session_state.sel_cat = c
                    st.session_state.page = 'details'
                    st.rerun()
            
            st.divider()
            if st.button("🚀 إرسال الطلب للشركة"):
                if st.session_state.cust_name:
                    order_text = f"طلبية: {st.session_state.cust_name}\nالتوقيت: {now}\n" + "\n".join(items_list)
                    url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(order_text)}"
                    st.markdown(f'<a href="{url}" target="_blank" class="wa-link"><div class="wa-button">فتح واتساب للإرسال النهائي ✅</div></a>', unsafe_allow_html=True)
                else:
                    st.error("الرجاء إدخال اسم المندوب")
