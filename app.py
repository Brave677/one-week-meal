import streamlit as st

st.title("1週間の献立管理アプリ")

# 曜日リスト
DAYS = ["月", "火", "水", "木", "金", "土", "日"]

# 初期値の献立データ
if "menu" not in st.session_state:
    st.session_state.menu = [
        {"day": day, "breakfast": "", "lunch": "", "dinner": ""} for day in DAYS
    ]

st.header("献立を入力してください")

for i, day in enumerate(DAYS):
    with st.expander(f"{day}曜日"):
        breakfast = st.text_input(f"{day}曜日の朝食", value=st.session_state.menu[i]["breakfast"], key=f"breakfast_{i}")
        lunch = st.text_input(f"{day}曜日の昼食", value=st.session_state.menu[i]["lunch"], key=f"lunch_{i}")
        dinner = st.text_input(f"{day}曜日の夕食", value=st.session_state.menu[i]["dinner"], key=f"dinner_{i}")
        if st.button(f"保存（{day}）", key=f"save_{i}"):
            st.session_state.menu[i]["breakfast"] = breakfast
            st.session_state.menu[i]["lunch"] = lunch
            st.session_state.menu[i]["dinner"] = dinner
            st.success(f"{day}曜日の献立を保存しました")

st.header("1週間の献立一覧")
st.table(st.session_state.menu)
