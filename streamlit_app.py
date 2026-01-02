import streamlit as st

st.title("تجربة نظام حلباوي")

if 'cart' not in st.session_state:
    st.session_state.cart = []

item = st.text_input("اسم الصنف التجريبي:")
qty = st.text_input("الكمية:")

if st.button("تثبيت"):
    st.session_state.cart.append(f"{item} - {qty}")
    st.success("تم التثبيت!")

st.write("المراجعة:", st.session_state.cart)
