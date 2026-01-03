import streamlit as st
import pandas as pd
import urllib.parse

# إعداد الصفحة
st.set_page_config(page_title="حلباوي إخوان", layout="wide")

# الرابط القوي الذي أثبت نجاحه مع ملفك
SHEET_ID = "1-Abj-Kvbe02az8KYZfQL0eal2arKw_wgjVQdJX06IA0"
# سحب ورقة "طلبات" حصراً
DIRECT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=طلبات"

@st.cache_data(ttl=1)
def load_data():
    try:
        # قراءة الأعمدة الخمسة (A, B, C, D, E)
        df = pd.read_csv(DIRECT_URL, header=None).dropna(how='all')
        df.columns = ['القسم', 'الوزن', 'الفئة', 'الاسم_للعرض', 'الاسم_العلمي']
        return df
    except:
        return None

df = load_data()

# تنسيق الواجهة لتناسب الجوال (تصميم نظيف وأزرار واضحة)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; direction: rtl; }
    .main-header { background-color: #1E3A8A; text-align: center; padding: 15px; border-radius: 12px; border-bottom: 4px solid #fca311; }
    .weight-header { background-color: #fca311; color: #1E3A8A; padding: 8px; border-radius: 5px; font-weight: bold; margin-top: 15px; text-align: center; font-size: 1.1rem; }
    .category-label { color: #fca311; font-weight: bold; margin-top: 10px; border-right: 3px solid #fca311; padding-right: 10px; }
    .item-card { background-color: #1c2333; padding: 10px; border-radius: 8px; border: 1px solid #2d3748; margin-bottom: 5px; font-size: 1rem; }
    input { background-color: #ffffcc !important; color: black !important; font-weight: bold !important; text-align: center !important; height: 45px !important; }
    .stButton button { border-radius: 10px; height: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# إدارة حالة التطبيق
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'page' not in st.session_state: st.session_state.page = 'home'

if df is not None:
    # --- الصفحة الرئيسية: الأقسام (حبوب، بهارات...) ---
    if st.session_state.page == 'home':
        st.markdown('<div class="main-header"><h1>طلبيات حلباوي إخوان</h1></div>', unsafe_allow_html=True)
        
        # خيار البحث السريع (اختياري)
        search_query = st.text_input("🔍 بحث سريع عن صنف:", placeholder="اكتب اسم الصنف هنا...")
        
        if search_query:
            results = df[df['الاسم_للعرض'].str.contains(search_query, na=False)]
            for _, r in results.iterrows():
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    with c1: st.markdown(f'<div class="item-card">{r["الاسم_للعرض"]} ({r["الوزن"]})</div>', unsafe_allow_html=True)
                    with c2: 
                        q = st.text_input("", key=f"src_{r['الاسم_العلمي']}", label_visibility="collapsed")
                        if q: st.session_state.cart[f"{r['الاسم_للعرض']} - {r['الوزن']}"] = q
        else:
            st.write("### 📂 الأقسام:")
            for cat in df['القسم'].unique():
                if st.button(f"📦 {cat}", use_container_width=True):
                    st.session_state.sel_cat = cat
                    st.session_state.page = 'details'
                    st.rerun()

        # --- أزرار المشاهدة والتثبيت في الأسفل ---
        if st.session_state.cart:
            st.markdown("---")
            st.markdown("### 🛒 الطلبية الحالية")
            for item, qty in list(st.session_state.cart.items()):
                st.write(f"✅ {item} ← الكمية: **{qty}**")
            
            customer = st.text_input("👤 اسم الزبون / المندوب:")
            
            col_send, col_clear = st.columns(2)
            with col_send:
                if st.button("✅ تثبيت وإرسال", type="primary", use_container_width=True):
                    if customer:
                        msg = f"طلبية من: *{customer}*\n" + "\n".join([f"• {k}: {v}" for k, v in st.session_state.cart.items()])
                        wa_url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25d366; color:white; padding:12px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">فتح واتساب</button></a>', unsafe_allow_html=True)
                    else:
                        st.warning("يرجى كتابة اسم الزبون")
            with col_clear:
                if st.button("🗑️ تفريغ السلة", use_container_width=True):
                    st.session_state.cart = {}
                    st.rerun()

    # --- صفحة التفاصيل: الترتيب (الوزن ثم الفئة ثم الصنف) ---
    elif st.session_state.page == 'details':
        cat = st.session_state.sel_cat
        st.markdown(f'<div class="main-header"><h2>{cat}</h2></div>', unsafe_allow_html=True)
        
        if st.button("🔙 عودة للقائمة الرئيسية"):
            st.session_state.page = 'home'
            st.rerun()

        cat_data = df[df['القسم'] == cat]
        
        # 1. الترتيب حسب الوزن (العمود B)
        for weight in cat_data['الوزن'].unique():
            st.markdown(f'<div class="weight-header">⚖️ أوزان {weight}</div>', unsafe_allow_html=True)
            
            weight_data = cat_data[cat_data['الوزن'] == weight]
            
            # 2. الترتيب حسب الفئة (العمود C)
            for sub_cat in weight_data['الفئة'].unique():
                st.markdown(f'<div class="category-label">📍 {sub_cat}</div>', unsafe_allow_html=True)
                
                final_items = weight_data[weight_data['الفئة'] == sub_cat]
                
                # 3. عرض الأصناف (العمود D)
                for _, row in final_items.iterrows():
                    col_name, col_input = st.columns([3, 1])
                    with col_name:
                        st.markdown(f'<div class="item-card">{row["الاسم_للعرض"]}</div>', unsafe_allow_html=True)
                    with col_input:
                        # المفتاح الفريد لمنع الأخطاء
                        unique_id = f"qty_{row['الاسم_العلمي']}_{row['الوزن']}"
                        # استرجاع القيمة إذا كانت موجودة مسبقاً
                        saved_val = st.session_state.cart.get(f"{row['الاسم_للعرض']} - {row['الوزن']}", "")
                        
                        val = st.text_input("", value=saved_val, key=unique_id, label_visibility="collapsed", placeholder="0")
                        
                        # التحديث التلقائي للسلة
                        if val and val.isdigit() and int(val) > 0:
                            st.session_state.cart[f"{row['الاسم_للعرض']} - {row['الوزن']}"] = val
                        elif val == "0" and f"{row['الاسم_للعرض']} - {row['الوزن']}" in st.session_state.cart:
                            del st.session_state.cart[f"{row['الاسم_للعرض']} - {row['الوزن']}"]

### المزايا في هذا الكود:
1.  **دقة البيانات:** يسحب الأعمدة (A, B, C, D, E) بالترتيب الذي حددته في الـ Sheet.
2.  **التنسيق الهرمي:** يفصل المنتجات أولاً حسب **الوزن** (عناوين صفراء)، ثم يضع **الفئة** كعنوان فرعي، ثم يدرج **الأصناف**.
3.  **أزرار التحكم:** زر "تثبيت وإرسال" و"تفريغ السلة" يظهران بوضوح في الصفحة الرئيسية عند اختيار أي صنف.
4.  **سهولة الطلب:** المندوب يكتب الكمية وتُحفظ تلقائياً، وعند الضغط على تثبيت، يفتح واتساب بالرسالة كاملة ومنسقة.

**هل الترتيب (أوزان 1000غ تحت بعضها ثم أوزان 500غ) هو ما كنت تقصده؟** استبدل الكود الآن وستجد الفرق فوراً.

