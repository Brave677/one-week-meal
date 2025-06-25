import streamlit as st

st.title("1週間の献立管理アプリ")

# 曜日リスト
DAYS = ["月", "火", "水", "木", "金", "土", "日"]

# メニューと材料のマッピング（例）
MENU_INGREDIENTS = {
    "カレー": ["米", "カレールー", "玉ねぎ", "にんじん", "じゃがいも", "肉"],
    "ハンバーグ": ["ひき肉", "玉ねぎ", "パン粉", "卵", "牛乳"],
    "味噌汁": ["味噌", "豆腐", "わかめ", "ねぎ"],
    "サラダ": ["レタス", "トマト", "きゅうり", "ドレッシング"],
    "焼き魚": ["魚", "レモン", "大根おろし"],
    "パスタ": ["パスタ", "トマトソース", "ベーコン", "にんにく"],
    "オムライス": ["米", "卵", "ケチャップ", "チキン"],
    "うどん": ["うどん", "だし", "ねぎ", "天ぷら"],
    "丼物": ["米", "肉", "玉ねぎ", "卵"],
    "スープ": ["野菜", "だし", "塩", "こしょう"]
}

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

# 買い物リスト生成機能
st.header("買い物リスト生成")

if st.button("買い物リストを生成"):
    # 全献立から材料を収集
    all_ingredients = []
    for day_menu in st.session_state.menu:
        for meal_type in ["breakfast", "lunch", "dinner"]:
            menu_name = day_menu[meal_type]
            if menu_name and menu_name in MENU_INGREDIENTS:
                all_ingredients.extend(MENU_INGREDIENTS[menu_name])
    
    # 材料の重複を除去してカウント
    ingredient_count = {}
    for ingredient in all_ingredients:
        ingredient_count[ingredient] = ingredient_count.get(ingredient, 0) + 1
    
    if ingredient_count:
        st.subheader("必要な材料")
        for ingredient, count in ingredient_count.items():
            st.write(f"• {ingredient}: {count}個")
    else:
        st.warning("献立が入力されていないか、定義されていないメニューです。")

# メニューと材料の一覧表示
with st.expander("メニューと材料の一覧"):
    for menu, ingredients in MENU_INGREDIENTS.items():
        st.write(f"**{menu}**: {', '.join(ingredients)}")
