import streamlit as st
import pandas as pd
import urllib.parse

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="طلبيات حلباوي", layout="wide")

# 2. الرابط المباشر لورقة "طلبات" (بناءً على ملفك)
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
SHEET_NAME = "طلبات"
DIRECT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"

@st.cache_data(ttl=1)
def load_data():
    try:
        # قراءة الأعمدة الخمسة كما في صورتك (القسم، الوزن، الفئة، الاسم، العلمي)
        df = pd.read_csv(DIRECT_URL, header=None).dropna(how='all')
        df = df.iloc[:, :5]
        df.columns = ['cat', 'pack', 'sub', 'name', 'sci']
        return df
    except Exception as e:
        return None

df = load_data()

# 3. تصميم الواجهة للهاتف (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 10px; border-bottom: 5px solid #fca311; margin-bottom: 20px; }
    .weight-title { background-color: #fca311; color: #1E3A8A; padding: 8px; border-radius: 8px; font-weight: bold; margin-top: 15px; text-align: center; }
    .sub-cat-label { color: #fca311; font-weight: bold; margin-top: 10px; border-right: 3px solid #fca311; padding-right: 10px; }
    .item-card { background-color: #1c2333; padding: 12px; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 8px; text-align: right; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; }
    .stButton button { background-color: #fca311; color: #1E3A8A !important; font-weight: bold; width: 100%; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is None or df.empty:
    st.error("⚠️ لم يتم العثور على بيانات في ورقة 'طلبات'.")
    if st.button("🔄 محاولة التحديث"):
        st.cache_data.clear()
        st.rerun()
else:
    # --- الصفحة الرئيسية (الأقسام) ---
    if st.session_state.page == 'home':
        st.markdown('<div class="header"><h1>طلبيات حلباوي</h1></div>', unsafe_allow_html=True)
        
        cats = df['cat'].unique()
        for c in cats:
            if st.button(f"📦 {c}"):
                st.session_state.sel_cat = c
                st.session_state.page = 'details'
                st.rerun()
        
        # قسم مشاهدة السلة وتثبيت الطلب
        if st.session_state.cart:
            st.markdown("---")
            with st.expander("🛒 مشاهدة الطلبية وتثبيتها", expanded=True):
                for item, qty in list(st.session_state.cart.items()):
                    st.write(f"✅ {item} : **{qty}**")
                
                cust = st.text_input("👤 اسم المندوب / الزبون:")
                if st.button("🚀 تثبيت وإرسال عبر واتساب"):
                    if cust:
                        order_msg = f"طلبية من: {cust}\n" + "\n".join([f"- {k}: {v}" for k, v in st.session_state.cart.items()])
                        url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(order_msg)}"
                        st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:15px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">تأكيد الإرسال ✅</button></a>', unsafe_allow_html=True)
                    else:
                        st.warning("يرجى إدخال اسم الزبون")
                
                if st.button("🗑️ تفريغ السلة"):
                    st.session_state.cart = {}
                    st.rerun()

    # --- صفحة التفاصيل (الترتيب الهرمي: وزن -> فئة -> صنف) ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        if st.button("🔙 عودة للقائمة"):
            st.session_state.page = 'home'
            st.rerun()

        filtered = df[df['cat'] == cat]
        
        # 1. الترتيب حسب الوزن (العمود B)
        for w in filtered['pack'].unique():
            st.markdown(f'<div class="weight-title">⚖️ قياس {w}</div>', unsafe_allow_html=True)
            w_df = filtered[filtered['pack'] == w]
            
            # 2. الترتيب حسب الفئة (العمود C)
            for s in w_df['sub'].unique():
                st.markdown(f'<div class="sub-cat-label">📍 {s}</div>', unsafe_allow_html=True)
                items = w_df[w_df['sub'] == s]
                
                # 3. عرض الأصناف (العمود D) مع خانة الكمية
                for _, row in items.iterrows():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f'<div class="item-card">{row["name"]}</div>', unsafe_allow_html=True)
                    with c2:
                        key = f"q_{row['name']}_{row['pack']}"
                        current = st.session_state.cart.get(f"{row['name']} ({row['pack']})", "")
                        val = st.text_input("", value=current, key=key, label_visibility="collapsed", placeholder="0")
                        
                        if val and val.isdigit() and int(val) > 0:
                            st.session_state.cart[f"{row['name']} ({row['pack']})"] = val
                        elif val == "0" and f"{row['name']} ({row['pack']})" in st.session_state.cart:
                            del st.session_state.cart[f"{row['name']} ({row['pack']})"]
