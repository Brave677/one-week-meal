import streamlit as st
import random

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
    "スープ": ["野菜", "だし", "塩", "こしょう"],
    "炒飯": ["米", "卵", "玉ねぎ", "にんじん"],
    "焼肉": ["肉", "レタス", "にんにく"],
    "天ぷら": ["魚", "天ぷら粉", "油"],
    "親子丼": ["米", "鶏肉", "卵", "玉ねぎ"],
    "麻婆豆腐": ["豆腐", "ひき肉", "にんにく", "豆板醤"]
}

# 初期値の献立データ
if "menu" not in st.session_state:
    st.session_state.menu = [
        {"day": day, "breakfast": "", "lunch": "", "dinner": ""} for day in DAYS
    ]

# 冷蔵庫の食材データ
if "fridge_ingredients" not in st.session_state:
    st.session_state.fridge_ingredients = {}

st.header("冷蔵庫の食材管理")

# 食材追加
col1, col2, col3 = st.columns(3)
with col1:
    new_ingredient = st.text_input("食材名")
with col2:
    new_quantity = st.number_input("数量", min_value=1, value=1)
with col3:
    if st.button("食材を追加"):
        if new_ingredient:
            st.session_state.fridge_ingredients[new_ingredient] = new_quantity
            st.success(f"{new_ingredient}を{new_quantity}個追加しました")

# 冷蔵庫の食材一覧と削除
st.subheader("現在の冷蔵庫の食材")
if st.session_state.fridge_ingredients:
    for ingredient, quantity in st.session_state.fridge_ingredients.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"• {ingredient}: {quantity}個")
        with col2:
            if st.button(f"削除", key=f"delete_{ingredient}"):
                del st.session_state.fridge_ingredients[ingredient]
                st.rerun()
        with col3:
            new_qty = st.number_input(f"数量変更", min_value=0, value=quantity, key=f"qty_{ingredient}")
            if new_qty != quantity:
                st.session_state.fridge_ingredients[ingredient] = new_qty
else:
    st.write("冷蔵庫に食材が登録されていません")

# 冷蔵庫の食材から献立作成機能
st.header("冷蔵庫の食材から献立作成")

def can_make_menu(menu_ingredients, fridge_ingredients):
    """冷蔵庫の食材でメニューが作れるかチェック"""
    for ingredient in menu_ingredients:
        if ingredient not in fridge_ingredients or fridge_ingredients[ingredient] <= 0:
            return False
    return True

def get_available_menus(fridge_ingredients):
    """冷蔵庫の食材で作れるメニューを取得"""
    available_menus = []
    for menu, ingredients in MENU_INGREDIENTS.items():
        if can_make_menu(ingredients, fridge_ingredients):
            available_menus.append(menu)
    return available_menus

# 作れるメニューの表示
if st.session_state.fridge_ingredients:
    available_menus = get_available_menus(st.session_state.fridge_ingredients)
    
    if available_menus:
        st.subheader("冷蔵庫の食材で作れるメニュー")
        for menu in available_menus:
            st.write(f"• {menu}")
        
        # 自動献立生成
        st.subheader("自動献立生成")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("1週間分の献立を自動生成"):
                # 冷蔵庫の食材をコピー（消費量を管理するため）
                temp_fridge = st.session_state.fridge_ingredients.copy()
                new_menu = []
                
                for day in DAYS:
                    day_menu = {"day": day, "breakfast": "", "lunch": "", "dinner": ""}
                    
                    # 各食事で作れるメニューをランダムに選択
                    for meal_type in ["breakfast", "lunch", "dinner"]:
                        available = get_available_menus(temp_fridge)
                        if available:
                            selected_menu = random.choice(available)
                            day_menu[meal_type] = selected_menu
                            
                            # 食材を消費
                            for ingredient in MENU_INGREDIENTS[selected_menu]:
                                temp_fridge[ingredient] -= 1
                    
                    new_menu.append(day_menu)
                
                st.session_state.menu = new_menu
                st.success("1週間分の献立を自動生成しました！")
        
        with col2:
            if st.button("献立をクリア"):
                st.session_state.menu = [
                    {"day": day, "breakfast": "", "lunch": "", "dinner": ""} for day in DAYS
                ]
                st.success("献立をクリアしました")
    else:
        st.warning("冷蔵庫の食材では作れるメニューがありません。")
else:
    st.info("冷蔵庫に食材を登録すると、自動で献立を作成できます。")

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
        st.subheader("必要な材料（冷蔵庫の食材を考慮）")
        
        # 冷蔵庫の食材を考慮した買い物リスト
        shopping_list = {}
        for ingredient, needed_count in ingredient_count.items():
            fridge_count = st.session_state.fridge_ingredients.get(ingredient, 0)
            remaining = needed_count - fridge_count
            if remaining > 0:
                shopping_list[ingredient] = remaining
            elif remaining < 0:
                st.info(f"✓ {ingredient}: 冷蔵庫に{fridge_count}個あり、{needed_count}個必要（余裕: {abs(remaining)}個）")
        
        if shopping_list:
            st.write("**買い物が必要な食材:**")
            for ingredient, count in shopping_list.items():
                st.write(f"• {ingredient}: {count}個")
        else:
            st.success("🎉 冷蔵庫の食材で全ての献立が作れます！")
    else:
        st.warning("献立が入力されていないか、定義されていないメニューです。")

# メニューと材料の一覧表示
with st.expander("メニューと材料の一覧"):
    for menu, ingredients in MENU_INGREDIENTS.items():
        st.write(f"**{menu}**: {', '.join(ingredients)}")
