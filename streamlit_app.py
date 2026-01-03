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

# 3. التنسيق المطور (خطوط أكبر وأزرار عريضة)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    [data-testid="stSidebar"] { display: none; }
    
    /* الخانة الزرقاء: تكبير الخط بشكل ملحوظ */
    .main-header { 
        background-color: #1E3A8A; 
        text-align: center; 
        padding: 30px 15px; 
        border-radius: 15px; 
        border-bottom: 8px solid #fca311; 
        margin-bottom: 25px; 
    }
    .main-header h1 { 
        margin: 0; 
        font-size: 35px !important; /* حجم كبير جداً */
        color: white; 
        font-weight: 900;
    }
    .main-header p { 
        margin: 10px 0 0 0; 
        font-size: 22px; 
        color: #fca311; 
        font-weight: bold; 
    }

    /* بيانات المندوب */
    .info-box {
        background-color: #1c2333;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d3748;
        margin-bottom: 25px;
        font-size: 16px;
        text-align: right;
    }
    
    .sub-category-header { 
        background-color: #2d3748; color: #fca311; padding: 10px; 
        border-radius: 5px; font-weight: bold; margin-top: 20px; 
        text-align: right; border-right: 8px solid #fca311; 
    }
    
    .item-label { 
        background-color: #1E3A8A; color: white; padding: 15px; 
        border-radius: 8px; font-weight: bold; text-align: right; margin-bottom: 3px;
        font-size: 18px;
    }
    
    input { 
        background-color: #ffffcc !important; color: black !important; 
        font-weight: bold !important; text-align: center !important; 
        height: 55px !important; border-radius: 8px !important; 
        font-size: 20px !important;
    }
    
    /* الأزرار الصفراء العريضة جداً */
    .stButton button { 
        background-color: #fca311 !important; 
        color: #1E3A8A !important; 
        font-weight: 900 !important; 
        border-radius: 12px !important; 
        height: 70px !important; /* زيادة الارتفاع */
        width: 100% !important; 
        display: block !important;
        font-size: 22px !important; /* تكبير الخط داخل الزر */
        margin-bottom: 15px !important;
        border: none !important;
    }
    
    /* زر العودة الخاص بالمراجعة */
    .secondary-btn button {
        background-color: #2d3748 !important;
        color: white !important;
        height: 50px !important;
        font-size: 16px !important;
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
        
        st.markdown(f'''
            <div class="info-box">
                🗓️ {now} <br>
                👤 المندوب: {st.session_state.cust_name if st.session_state.cust_name else "---"}
            </div>
        ''', unsafe_allow_html=True)

        st.session_state.cust_name = st.text_input("ادخل اسم المندوب / الزبون هنا:", value=st.session_state.cust_name)
        
        st.write("### 📂 الأقسام المتاحة:")
        for c in df['cat'].unique():
            if st.button(f"📦 قسم {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        if st.session_state.cart:
            st.divider()
            if st.button("🛒 مراجعة وتثبيت الطلب"):
                st.session_state.page = 'review'
                st.rerun()

    # --- صفحة التفاصيل ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="main-header"><h1>{cat}</h1><p>شركة حلباوي إخوان</p></div>', unsafe_allow_html=True)
        
        if st.button("🔙 العودة للقائمة الرئيسية"):
            st.session_state.page = 'home'
            st.rerun()

        cat_df = df[df['cat'] == cat]
        for weight in cat_df['pack'].unique():
            with st.expander(f"🔽 {weight}", expanded=True):
                w_df = cat_df[cat_df['pack'] == weight]
                for sub in w_df['sub'].unique():
                    st.markdown(f'<div class="sub-category-header">{sub}</div>', unsafe_allow_html=True)
                    items = w_df[w_df['sub'] == sub]
                    for _, row in items.iterrows():
                        st.markdown(f'<div class="item-label">{row["name"]}</div>', unsafe_allow_html=True)
                        key = f"q_{row['name']}_{row['pack']}"
                        curr = st.session_state.cart.get(key, {}).get('qty', "")
                        val = st.text_input("", value=curr, key=key+"_v", label_visibility="collapsed", placeholder="0")
                        if val:
                            st.session_state.cart[key] = {'name': row['name'], 'qty': val, 'cat': row['cat']}
                        elif val == "" and key in st.session_state.cart:
                            del st.session_state.cart[key]
        
        st.divider()
        if st.button("✅ إنهاء مراجعة هذا القسم"):
            st.session_state.page = 'review'
            st.rerun()

    # --- صفحة المراجعة النهائية (مع خيارات العودة للأقسام) ---
    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>مراجعة وتثبيت</h1><p>حلباوي إخوان</p></div>', unsafe_allow_html=True)
        
        if not st.session_state.cart:
            st.warning("السلة فارغة")
            if st.button("🏠 العودة للرئيسية"):
                st.session_state.page = 'home'
                st.rerun()
        else:
            st.markdown(f"**👤 المندوب:** {st.session_state.cust_name} <br> **⏰ التوقيت:** {now}", unsafe_allow_html=True)
            st.write("---")
            
            final_msg = []
            for k, v in st.session_state.cart.items():
                st.markdown(f"✅ {v['name']} : **{v['qty']}**")
                final_msg.append(f"{v['name']}: {v['qty']}")
            
            st.divider()
            
            # قسم "تعديل أو إضافة" داخل صفحة المراجعة
            st.write("### ➕ هل تريد إضافة المزيد؟")
            for c in df['cat'].unique():
                if st.button(f"العودة لـ {c}"):
                    st.session_state.sel_cat = c
                    st.session_state.page = 'details'
                    st.rerun()
            
            st.divider()
            
            if st.button("🚀 إرسال الطلبية النهائية عبر واتساب"):
                if st.session_state.cust_name:
                    order_text = f"طلبية: {st.session_state.cust_name}\nالتوقيت: {now}\n" + "\n".join(final_msg)
                    url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(order_text)}"
                    st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:20px; border-radius:15px; border:none; font-weight:bold; cursor:pointer; font-size:22px;">تأكيد الإرسال النهائي ✅</button></a>', unsafe_allow_html=True)
                else:
                    st.error("الرجاء إدخال اسم المندوب في الصفحة الرئيسية أولاً")
