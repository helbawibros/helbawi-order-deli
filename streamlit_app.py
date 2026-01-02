import streamlit as st
import urllib.parse
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(page_title="طلب مبيعات - حلباوي إخوان", layout="wide")

# 2. تصميم الواجهة لتشبه الورقة الرسمية
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .category-header { 
        background-color: #1E3A8A; color: white; padding: 10px; border-radius: 5px; 
        font-weight: bold; font-size: 18px; margin-top: 20px; text-align: center;
    }
    .sub-category {
        background-color: #e9ecef; color: #1E3A8A; padding: 5px; font-weight: bold;
        border-right: 5px solid #fca311; margin-top: 10px; text-align: right;
    }
    .item-label { font-size: 16px; font-weight: 500; color: #333; }
    input { font-size: 18px !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📋 نموذج طلب مبيعات")
st.write(f"التاريخ: {datetime.now().strftime('%Y-%m-%d')}")

# معلومات أساسية
col_info1, col_info2 = st.columns(2)
with col_info1:
    delegate = st.selectbox("👤 اسم المندوب:", ["مندوب 1", "مندوب 2", "المندوب النشيط"])
with col_info2:
    customer = st.text_input("🏢 اسم الزبون:")

# دالة لتوليد الأسطر
def render_item_row(item_name):
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f'<p class="item-label">{item_name}</p>', unsafe_allow_html=True)
    with c2:
        return st.number_input("", min_value=0, step=1, key=item_name, label_visibility="collapsed")

order_data = {}

# --- القائمة الرئيسية (حسب الورقة) ---
tab1, tab2 = st.tabs(["🌾 الحبوب والبقوليات", "🌶️ البهارات والأصناف الأخرى"])

with tab1:
    # تعبئة 1000غ
    st.markdown('<div class="category-header">تعبئة 1000غ / 907غ</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sub-category">حمص</div>', unsafe_allow_html=True)
    for i in ["حمص فجلي - 12", "حمص محمص - 10", "حمص فجلي - 9", "حمص كسر"]:
        q = render_item_row(i)
        if q > 0: order_data[i] = q

    st.markdown('<div class="sub-category">فول / فاصوليا</div>', unsafe_allow_html=True)
    for i in ["فول حب", "فول مجروش", "فول عريض", "فاصوليا صنوبرية", "فاصوليا حمراء طويلة"]:
        q = render_item_row(i)
        if q > 0: order_data[i] = q

    st.markdown('<div class="sub-category">عدس</div>', unsafe_allow_html=True)
    for i in ["عدس أبيض رفيع", "عدس أحمر", "عدس أحمر موردي", "عدس مجروش", "عدس عريض"]:
        q = render_item_row(i)
        if q > 0: order_data[i] = q

with tab2:
    st.markdown('<div class="category-header">تعبئة 500غ / 200غ</div>', unsafe_allow_html=True)
    # يمكنك إضافة بقية الأصناف هنا تدريجياً بنفس الطريقة
    st.info("سيتم إضافة بقية أصناف البهارات بناءً على الجدول الورقي.")

# زر الإرسال
st.divider()
if st.button("🚀 إرسال الطلبية الآن", use_container_width=True):
    if not customer:
        st.error("الرجاء إدخال اسم الزبون!")
    elif not order_data:
        st.warning("الطلبية فارغة!")
    else:
        # تجهيز رسالة الواتساب
        msg = f"طلب مبيعات جديد\nالمندوب: {delegate}\nالزبون: {customer}\n"
        msg += "-"*20 + "\n"
        for item, qty in order_data.items():
            msg += f"• {item}: {qty}\n"
        
        # رابط واتساب (رقمك الموجود بالكود القديم)
        whatsapp_url = f"https://api.whatsapp.com/send?phone=9613220893&text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; text-align:center; border-radius:10px; font-weight:bold;">تأكيد عبر واتساب</div></a>', unsafe_allow_html=True)
