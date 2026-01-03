import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام طلبيات حلباوي", layout="centered")

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

# 3. التنسيق (تصميم العناوين والأزرار العريضة)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    [data-testid="stSidebar"] { display: none; }
    
    /* العنوان الرئيسي المحدث */
    .main-header { 
        background-color: #1E3A8A; 
        text-align: center; 
        padding: 20px; 
        border-radius: 10px; 
        border-bottom: 5px solid #fca311; 
        margin-bottom: 20px; 
    }
    .main-header h1 { margin: 0; font-size: 22px; color: white; }
    .main-header p { margin: 5px 0 0 0; font-size: 18px; color: #fca311; font-weight: bold; }

    /* بيانات المندوب */
    .info-box {
        background-color: #1c2333;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #2d3748;
        margin-bottom: 20px;
        font-size: 14px;
    }
    
    .sub-category-header { 
        background-color: #2d3748; color: #fca311; padding: 8px; 
        border-radius: 5px; font-weight: bold; margin-top: 15px; 
        text-align: right; border-right: 5px solid #fca311; 
    }
    
    .item-label { 
        background-color: #1E3A8A; color: white; padding: 12px; 
        border-radius: 5px; font-weight: bold; text-align: right; margin-bottom: 2px;
    }
    
    input { 
        background-color: #ffffcc !important; color: black !important; 
        font-weight: bold !important; text-align: center !important; 
        height: 48px !important; border-radius: 5px !important; 
    }
    
    /* جعل الأزرار كبيرة وعلى كامل السطر */
    .stButton button { 
        background-color: #fca311; color: #1E3A8A !important; 
        font-weight: bold; border-radius: 10px; height: 60px; 
        width: 100% !important; border: none; font-size: 18px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# إدارة الحالة
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'
# افتراضياً الاسم فارغ ليتم ربطه لاحقاً ببرنامج الفواتير
if 'cust_name' not in st.session_state: st.session_state.cust_name = ""

# التوقيت الحالي
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
        
        # عرض بيانات المندوب (الاسم، التاريخ، الساعة)
        st.markdown(f'''
            <div class="info-box">
                🗓️ التاريخ والوقت: {now} <br>
                👤 المندوب: {st.session_state.cust_name if st.session_state.cust_name else "يرجى إدخال الاسم"}
            </div>
        ''', unsafe_allow_html=True)

        st.session_state.cust_name = st.text_input("تعديل اسم المندوب / الزبون:", value=st.session_state.cust_name)
        
        st.write("### 📂 اختر القسم:")
        # عرض الأقسام كأزرار كبيرة تحت بعضها
        for c in df['cat'].unique():
            if st.button(f"📦 {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        if st.session_state.cart:
            st.divider()
            if st.button("🛒 مراجعة الطلبية الكاملة والإرسال"):
                st.session_state.page = 'review'
                st.rerun()

    # --- صفحة التفاصيل ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="main-header"><h1>{cat}</h1><p>شركة حلباوي إخوان</p></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 الرئيسية"):
                st.session_state.page = 'home'
                st.rerun()
        with col2:
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
                        st.markdown(f'<div class="item-label">{row["name"]}</div>', unsafe_allow_html=True)
                        key = f"q_{row['name']}_{row['pack']}"
                        curr = st.session_state.cart.get(key, {}).get('qty', "")
                        val = st.text_input("", value=curr, key=key+"_v", label_visibility="collapsed", placeholder="أدخل العدد")
                        if val:
                            st.session_state.cart[key] = {'name': row['name'], 'qty': val}
                        elif val == "" and key in st.session_state.cart:
                            del st.session_state.cart[key]

    # --- صفحة المراجعة ---
    elif st.session_state.page == 'review':
        st.markdown('<div class="main-header"><h1>مراجعة الطلبية</h1><p>حلباوي إخوان</p></div>', unsafe_allow_html=True)
        
        if not st.session_state.cart:
            st.warning("السلة فارغة")
            if st.button("🔙 عودة"):
                st.session_state.page = 'home'
                st.rerun()
        else:
            st.markdown(f"**المندوب:** {st.session_state.cust_name} | **التوقيت:** {now}")
            st.write("---")
            final_msg = []
            for k, v in st.session_state.cart.items():
                st.markdown(f"✅ {v['name']} : **{v['qty']}**")
                final_msg.append(f"{v['name']}: {v['qty']}")
            
            st.divider()
            if st.button("🚀 إرسال الطلبية كاملة"):
                if st.session_state.cust_name:
                    order_text = f"طلبية: {st.session_state.cust_name}\nالتوقيت: {now}\n" + "\n".join(final_msg)
                    url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(order_text)}"
                    st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">فتح واتساب ✅</button></a>', unsafe_allow_html=True)
                else:
                    st.error("الرجاء التأكد من اسم المندوب")

