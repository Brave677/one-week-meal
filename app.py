import streamlit as st

st.title("サンプルWebアプリ")

input_message = st.text_input(label="入力した文字数を表示します。")

text_count = len(input_message)

if st.button("実行する"):

    st.write(f"文字数: **{text_count}**")
