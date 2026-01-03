import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="طلبيات حلباوي", layout="wide")

# 2. جلب البيانات
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

# 3. التصميم المتقدم لإزالة "الزيح" والفراغات
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    
    /* إزالة الفراغات بين الأعمدة */
    [data-testid="column"] { padding: 0px !important; margin: 0px !important; }
    div[data-testid="stHorizontalBlock"] { gap: 5px !important; }

    .main-header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 10px; border-bottom: 5px solid #fca311; margin-bottom: 15px; }
    
    .sub-category-header { background-color: #2d3748; color: #fca311; padding: 8px; border-radius: 5px; font-weight: bold; margin-top: 10px; text-align: right; border-right: 5px solid #fca311; }
    
    /* تنسيق مربع الصنف الأزرق ليكون متلاصقاً مع الكمية */
    .item-label { 
        background-color: #1E3A8A; 
        color: white; 
        padding: 10px; 
        border-radius: 5px; 
        font-weight: bold; 
        text-align: right; 
        margin-bottom: 0px !important;
        display: flex;
        align-items: center;
        height: 45px;
    }

    /* تنسيق خانة الإدخال الصفراء */
    input { 
        background-color: #ffffcc !important; 
        color: black !important; 
        font-weight: bold !important; 
        text-align: center !important; 
        height: 45px !important; 
        border: none !important;
        border-radius: 5px !important;
    }

    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; border-radius: 10px; height: 50px; width: 100%; }
    
    /* إخفاء الهوامش العلوية لخانة الإدخال */
    div[data-testid="stTextInput"] { margin-top: 0px !important; padding-top: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cust_name' not in st.session_state: st.session_state.cust_name = ""

if df is not None:
    # --- القائمة الجانبية ---
    with st.sidebar:
        st.markdown("### 📋 التحكم")
        if st.button("🏠 القائمة الرئيسية"):
            st.session_state.page = 'home'
            st.rerun()
        if st.button("🛒 مراجعة الطلبية"):
            st.session_state.page = 'review'
            st.rerun()
        st.divider()
        st.session_state.cust_name = st.text_input("👤 اسم الزبون:", value=st.session_state.cust_name)

    # --- الصفحة الرئيسية ---
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>طلبيات حلباوي</h1></div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for idx, c in enumerate(df['cat'].unique()):
            with cols[idx % 2]:
                if st.button(f"📦 {c}"):
                    st.session_state.sel_cat = c
                    st.session_state.page = 'details'
                    st.rerun()

    # --- صفحة التفاصيل (إصلاح الزيح) ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="main-header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        if st.button("✅ تثبيت ومراجعة الطلب الكامل"):
            st.session_state.page = 'review'
            st.rerun()

        cat_df = df[df['cat'] == cat]
        for weight in cat_df['pack'].unique():
            with st.expander(f"🔽 {weight}", expanded=True):
                w_df = cat_df[cat_df['pack'] == weight]
                for sub in w_df['sub'].unique():
                    st.markdown(f'<div class="sub-category-header">{sub}</div>', unsafe_allow_html=True)
                    items = w_df[w_df['sub'] == sub]
                    for _, row in items.iterrows():
                        # استخدام أعمدة متلاصقة جداً [4, 1] لتصغير الفجوة
                        c1, c2 = st.columns([4, 1.2])
                        with c1:
                            st.markdown(f'<div class="item-label">{row["name"]}</div>', unsafe_allow_html=True)
                        with c2:
                            key = f"q_{row['name']}_{row['pack']}"
                            curr = st.session_state.cart.get(key, {}).get('qty', "")
                            val = st.text_input("", value=curr, key=key+"_v", label_visibility="collapsed")
                            if val:
                                st.session_state.cart[key] = {'name': row['name'], 'qty': val}
                            elif val == "" and key in st.session_state.cart:
                                del st.session_state.cart[key]

    # --- صفحة المراجعة ---
    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>مراجعة الطلبية</h1></div>', unsafe_allow_html=True)
        if not st.session_state.cart:
            st.warning("السلة فارغة")
            if st.button("🔙 عودة"):
                st.session_state.page = 'home'
                st.rerun()
        else:
            st.write(f"👤 **الزبون:** {st.session_state.cust_name}")
            final_list = []
            for k, v in st.session_state.cart.items():
                st.markdown(f"🔹 **{v['name']}** ← `{v['qty']}`")
                final_list.append(f"{v['name']}: {v['qty']}")
            
            if st.button("🚀 إرسال عبر واتساب"):
                if st.session_state.cust_name:
                    msg = f"طلبية: {st.session_state.cust_name}\n" + "\n".join(final_list)
                    url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold;">تأكيد وفتح واتساب ✅</button></a>', unsafe_allow_html=True)
                else:
                    st.error("أدخل اسم الزبون أولاً")
