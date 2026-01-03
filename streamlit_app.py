import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة الأساسية (بدون أي تعقيدات)
st.set_page_config(page_title="طلبيات حلباوي", layout="centered")

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

# 3. تنسيق الواجهة (CSS) - نسخة محسنة لمنع "الزيح"
st.markdown("""
    <style>
    /* منع أي هوامش جانبية تسبب الخطوط العمودية */
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    [data-testid="stSidebar"] { display: none; } /* إخفاء القائمة الجانبية تماماً لمنع الانزياح */
    
    .main-header { 
        background-color: #1E3A8A; 
        text-align: center; 
        padding: 15px; 
        border-radius: 10px; 
        border-bottom: 5px solid #fca311; 
        margin-bottom: 20px; 
    }
    
    .sub-category-header { 
        background-color: #2d3748; 
        color: #fca311; 
        padding: 8px; 
        border-radius: 5px; 
        font-weight: bold; 
        margin-top: 15px; 
        text-align: right; 
        border-right: 5px solid #fca311; 
    }
    
    .item-label { 
        background-color: #1E3A8A; 
        color: white; 
        padding: 12px; 
        border-radius: 5px; 
        font-weight: bold; 
        text-align: right; 
        margin-bottom: 2px;
    }
    
    input { 
        background-color: #ffffcc !important; 
        color: black !important; 
        font-weight: bold !important; 
        text-align: center !important; 
        height: 48px !important; 
        border-radius: 5px !important; 
    }
    
    .stButton button { 
        background-color: #fca311; 
        color: #1E3A8A !important; 
        font-weight: bold; 
        border-radius: 10px; 
        height: 55px; 
        width: 100%; 
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# إدارة حالة التطبيق
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'cust_name' not in st.session_state: st.session_state.cust_name = ""

if df is not None:
    # --- الصفحة الرئيسية ---
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>طلبيات حلباوي</h1></div>', unsafe_allow_html=True)
        
        st.session_state.cust_name = st.text_input("👤 اسم المندوب / الزبون:", value=st.session_state.cust_name)
        
        st.write("### 📂 الأقسام:")
        for c in df['cat'].unique():
            if st.button(f"📦 {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        if st.session_state.cart:
            st.divider()
            if st.button("🛒 مراجعة الطلبية الكاملة وإرسالها"):
                st.session_state.page = 'review'
                st.rerun()

    # --- صفحة التفاصيل ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="main-header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        # أزرار تحكم علوية متساوية
        c_nav1, c_nav2 = st.columns(2)
        with c_nav1:
            if st.button("🏠 الرئيسية"):
                st.session_state.page = 'home'
                st.rerun()
        with c_nav2:
            if st.button("🛒 مراجعة"):
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
                        # عرض الاسم والكمية تحت بعض أو بجانب بعض بشكل بسيط جداً لمنع التداخل
                        st.markdown(f'<div class="item-label">{row["name"]}</div>', unsafe_allow_html=True)
                        key = f"q_{row['name']}_{row['pack']}"
                        curr = st.session_state.cart.get(key, {}).get('qty', "")
                        val = st.text_input("", value=curr, key=key+"_v", label_visibility="collapsed", placeholder="أدخل العدد")
                        if val:
                            st.session_state.cart[key] = {'name': row['name'], 'qty': val}
                        elif val == "" and key in st.session_state.cart:
                            del st.session_state.cart[key]

    # --- صفحة المراجعة النهائية ---
    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>مراجعة الطلب</h1></div>', unsafe_allow_html=True)
        
        if not st.session_state.cart:
            st.warning("لم تختر أي أصناف")
            if st.button("🔙 عودة"):
                st.session_state.page = 'home'
                st.rerun()
        else:
            st.write(f"👤 **الزبون:** {st.session_state.cust_name}")
            final_msg = []
            for k, v in st.session_state.cart.items():
                st.markdown(f"✅ {v['name']} : **{v['qty']}**")
                final_msg.append(f"{v['name']}: {v['qty']}")
            
            st.divider()
            if st.button("🚀 إرسال عبر واتساب"):
                if st.session_state.cust_name:
                    order_text = f"طلبية: {st.session_state.cust_name}\n" + "\n".join(final_msg)
                    url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(order_text)}"
                    st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold;">تأكيد وفتح واتساب ✅</button></a>', unsafe_allow_html=True)
                else:
                    st.error("يرجى كتابة اسم الزبون أولاً")
            
            if st.button("➕ إضافة أصناف أخرى"):
                st.session_state.page = 'home'
                st.rerun()
