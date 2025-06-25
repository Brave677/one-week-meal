import streamlit as st
import random
import openai
import json

st.title("One-week-meal")

# OpenAI API設定
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""

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

# メニューの詳細情報（カロリー、調理時間、ジャンル、アレルギー）
MENU_DETAILS = {
    "カレー": {"calories": 800, "cook_time": 30, "genre": "洋食", "allergens": ["小麦"]},
    "ハンバーグ": {"calories": 600, "cook_time": 25, "genre": "洋食", "allergens": ["卵", "小麦"]},
    "味噌汁": {"calories": 100, "cook_time": 10, "genre": "和食", "allergens": []},
    "サラダ": {"calories": 150, "cook_time": 5, "genre": "洋食", "allergens": []},
    "焼き魚": {"calories": 400, "cook_time": 20, "genre": "和食", "allergens": []},
    "パスタ": {"calories": 700, "cook_time": 15, "genre": "洋食", "allergens": ["小麦"]},
    "オムライス": {"calories": 500, "cook_time": 20, "genre": "洋食", "allergens": ["卵"]},
    "うどん": {"calories": 450, "cook_time": 10, "genre": "和食", "allergens": ["小麦"]},
    "丼物": {"calories": 600, "cook_time": 15, "genre": "和食", "allergens": ["卵"]},
    "スープ": {"calories": 200, "cook_time": 15, "genre": "洋食", "allergens": []},
    "炒飯": {"calories": 550, "cook_time": 20, "genre": "中華", "allergens": ["卵"]},
    "焼肉": {"calories": 700, "cook_time": 30, "genre": "韓国料理", "allergens": []},
    "天ぷら": {"calories": 500, "cook_time": 25, "genre": "和食", "allergens": ["小麦", "卵"]},
    "親子丼": {"calories": 650, "cook_time": 20, "genre": "和食", "allergens": ["卵"]},
    "麻婆豆腐": {"calories": 400, "cook_time": 20, "genre": "中華", "allergens": []}
}

# 初期値の献立データ
if "menu" not in st.session_state:
    st.session_state.menu = [
        {"day": day, "breakfast": "", "lunch": "", "dinner": ""} for day in DAYS
    ]

# 冷蔵庫の食材データ
if "fridge_ingredients" not in st.session_state:
    st.session_state.fridge_ingredients = {}

# 献立条件データ
if "menu_conditions" not in st.session_state:
    st.session_state.menu_conditions = {
        "max_calories": 2000,
        "max_cook_time": 60,
        "preferred_genres": [],
        "allergies": [],
        "avoid_ingredients": []
    }

# サイドバーでAPIキー設定
with st.sidebar:
    st.header("設定")
    st.subheader("OpenAI API設定")
    api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key)
    if api_key != st.session_state.openai_api_key:
        st.session_state.openai_api_key = api_key
        if api_key:
            st.success("APIキーを設定しました")
    
    if st.session_state.openai_api_key:
        st.success("✅ APIキーが設定されています")
    else:
        st.warning("⚠️ APIキーを設定してください")

    st.subheader("献立条件設定")
    # 条件設定フォーム
    max_calories = st.number_input("1日の最大カロリー", min_value=500, max_value=5000, value=st.session_state.menu_conditions["max_calories"])
    max_cook_time = st.number_input("最大調理時間（分）", min_value=5, max_value=180, value=st.session_state.menu_conditions["max_cook_time"])
    
    # 好みのジャンル
    all_genres = list(set([details["genre"] for details in MENU_DETAILS.values()]))
    preferred_genres = st.multiselect(
        "好みの料理ジャンル",
        all_genres,
        default=st.session_state.menu_conditions["preferred_genres"]
    )
    
    # アレルギー
    all_allergens = []
    for details in MENU_DETAILS.values():
        all_allergens.extend(details["allergens"])
    all_allergens = list(set(all_allergens))
    
    allergies = st.multiselect(
        "アレルギー",
        all_allergens,
        default=st.session_state.menu_conditions["allergies"]
    )

    # 避けたい食材
    avoid_ingredients = st.multiselect(
        "避けたい食材",
        ["肉", "魚", "卵", "乳製品", "小麦", "大豆"],
        default=st.session_state.menu_conditions["avoid_ingredients"]
    )
    
    # 条件保存
    if st.button("条件を保存"):
        st.session_state.menu_conditions = {
            "max_calories": max_calories,
            "max_cook_time": max_cook_time,
            "preferred_genres": preferred_genres,
            "allergies": allergies,
            "avoid_ingredients": avoid_ingredients
        }
        st.success("献立条件を保存しました")

    st.subheader("冷蔵庫の食材管理")
    # 食材追加
    new_ingredient = st.text_input("食材名")
    new_quantity = st.number_input("数量", min_value=1, value=1)
    if st.button("食材を追加"):
        if new_ingredient:
            st.session_state.fridge_ingredients[new_ingredient] = new_quantity
            st.success(f"{new_ingredient}を{new_quantity}個追加しました")

    # 冷蔵庫の食材一覧と削除
    if st.session_state.fridge_ingredients:
        for ingredient, quantity in st.session_state.fridge_ingredients.items():
            st.write(f"• {ingredient}: {quantity}個")
            if st.button(f"削除 {ingredient}", key=f"delete_{ingredient}"):
                del st.session_state.fridge_ingredients[ingredient]
                st.rerun()

# 現在の条件表示
st.subheader("現在の条件")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**最大カロリー:** {st.session_state.menu_conditions['max_calories']}kcal")
    st.write(f"**最大調理時間:** {st.session_state.menu_conditions['max_cook_time']}分")
with col2:
    st.write(f"**好みのジャンル:** {', '.join(st.session_state.menu_conditions['preferred_genres']) if st.session_state.menu_conditions['preferred_genres'] else '指定なし'}")
    st.write(f"**アレルギー:** {', '.join(st.session_state.menu_conditions['allergies']) if st.session_state.menu_conditions['allergies'] else 'なし'}")

# AI献立生成機能
st.header("AI献立生成")

def generate_ai_menu():
    """OpenAI APIを使って献立を生成"""
    if not st.session_state.openai_api_key:
        st.error("OpenAI APIキーが設定されていません")
        return None
    
    try:
        openai.api_key = st.session_state.openai_api_key
        
        # プロンプトの作成
        prompt = f"""
以下の条件に基づいて1週間分の献立（朝食・昼食・夕食）を提案してください。

【冷蔵庫にある食材】
{', '.join([f"{ingredient}({quantity}個)" for ingredient, quantity in st.session_state.fridge_ingredients.items()]) if st.session_state.fridge_ingredients else "なし"}

【条件】
- 1日の最大カロリー: {st.session_state.menu_conditions['max_calories']}kcal
- 最大調理時間: {st.session_state.menu_conditions['max_cook_time']}分
- 好みのジャンル: {', '.join(st.session_state.menu_conditions['preferred_genres']) if st.session_state.menu_conditions['preferred_genres'] else '指定なし'}
- アレルギー: {', '.join(st.session_state.menu_conditions['allergies']) if st.session_state.menu_conditions['allergies'] else 'なし'}
- 避けたい食材: {', '.join(st.session_state.menu_conditions['avoid_ingredients']) if st.session_state.menu_conditions['avoid_ingredients'] else 'なし'}

【出力形式】
以下のJSON形式で出力してください：
{{
    "menu": [
        {{
            "day": "月",
            "breakfast": "メニュー名",
            "lunch": "メニュー名", 
            "dinner": "メニュー名"
        }},
        ...
    ]
}}

冷蔵庫の食材を優先的に使用し、栄養バランスを考慮した献立を提案してください。
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[ 
                {"role": "system", "content": "あなたは栄養士で料理の専門家です。与えられた条件に基づいて最適な献立を提案してください。"},
                {"role": "user", "content": prompt}
            ],
         temperature=0.7
          )
        
        # レスポンスからJSONを抽出
        content = response.choices[0].message.content
        # JSON部分を抽出（```json と ``` の間）
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
        else:
            # JSON部分を直接探す
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            json_str = content[json_start:json_end]
        
        menu_data = json.loads(json_str)
        return menu_data["menu"]
        
    except Exception as e:
        st.error(f"AI献立生成でエラーが発生しました: {str(e)}")
        return None

# AI献立生成ボタン
col1, col2 = st.columns(2)
with col1:
    if st.button("AIで献立を生成", disabled=not st.session_state.openai_api_key):
        with st.spinner("AIが献立を生成中..."):
            ai_menu = generate_ai_menu()
            if ai_menu:
                st.session_state.menu = ai_menu
                st.success("AIが献立を生成しました！")

with col2:
    if st.button("献立をクリア"):
        st.session_state.menu = [
            {"day": day, "breakfast": "", "lunch": "", "dinner": ""} for day in DAYS
        ]
        st.success("献立をクリアしました")

# 冷蔵庫の食材から献立作成機能
st.header("冷蔵庫の食材から献立作成")

def can_make_menu(menu_ingredients, fridge_ingredients):
    """冷蔵庫の食材でメニューが作れるかチェック"""
    for ingredient in menu_ingredients:
        if ingredient not in fridge_ingredients or fridge_ingredients[ingredient] <= 0:
            return False
    return True

def check_menu_conditions(menu_name, conditions):
    """メニューが条件に合うかチェック"""
    if menu_name not in MENU_DETAILS:
        return False
    
    details = MENU_DETAILS[menu_name]
    
    # カロリーチェック
    if details["calories"] > conditions["max_calories"]:
        return False
    
    # 調理時間チェック
    if details["cook_time"] > conditions["max_cook_time"]:
        return False
    
    # アレルギーチェック
    for allergen in conditions["allergies"]:
        if allergen in details["allergens"]:
            return False
    
    # 避けたい食材チェック
    for avoid_ingredient in conditions["avoid_ingredients"]:
        if avoid_ingredient in MENU_INGREDIENTS[menu_name]:
            return False
    
    return True

def get_available_menus(fridge_ingredients, conditions=None):
    """冷蔵庫の食材で作れるメニューを取得（条件付き）"""
    available_menus = []
    for menu, ingredients in MENU_INGREDIENTS.items():
        if can_make_menu(ingredients, fridge_ingredients):
            if conditions is None or check_menu_conditions(menu, conditions):
                available_menus.append(menu)
    return available_menus

# 作れるメニューの表示
if st.session_state.fridge_ingredients:
    available_menus = get_available_menus(st.session_state.fridge_ingredients, st.session_state.menu_conditions)
    
    if available_menus:
        st.subheader("条件に合う作れるメニュー")
        for menu in available_menus:
            details = MENU_DETAILS[menu]
            st.write(f"• {menu} (カロリー: {details['calories']}kcal, 調理時間: {details['cook_time']}分, ジャンル: {details['genre']})")
        
        # 自動献立生成
        st.subheader("条件付き自動献立生成")
        if st.button("条件付きで1週間分の献立を自動生成"):
            # 冷蔵庫の食材をコピー（消費量を管理するため）
            temp_fridge = st.session_state.fridge_ingredients.copy()
            new_menu = []
            
            for day in DAYS:
                day_menu = {"day": day, "breakfast": "", "lunch": "", "dinner": ""}
                day_calories = 0
                
                # 各食事で作れるメニューをランダムに選択
                for meal_type in ["breakfast", "lunch", "dinner"]:
                    available = get_available_menus(temp_fridge, st.session_state.menu_conditions)
                    if available:
                        # カロリー制限を考慮してメニューを選択
                        suitable_menus = []
                        for menu in available:
                            remaining_calories = st.session_state.menu_conditions["max_calories"] - day_calories
                            if MENU_DETAILS[menu]["calories"] <= remaining_calories:
                                suitable_menus.append(menu)
                        
                        if suitable_menus:
                            selected_menu = random.choice(suitable_menus)
                            day_menu[meal_type] = selected_menu
                            day_calories += MENU_DETAILS[selected_menu]["calories"]
                            
                            # 食材を消費
                            for ingredient in MENU_INGREDIENTS[selected_menu]:
                                temp_fridge[ingredient] -= 1
                
                new_menu.append(day_menu)
            
            st.session_state.menu = new_menu
            st.success("条件付きで1週間分の献立を自動生成しました！")
    else:
        st.warning("冷蔵庫の食材と条件では作れるメニューがありません。")
else:
    st.info("冷蔵庫に食材を登録すると、条件付きで献立を作成できます。")

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

# 献立の栄養・調理時間サマリー
if any(any(meal for meal in day.values() if meal != "" and meal != day["day"]) for day in st.session_state.menu):
    st.subheader("献立サマリー")
    total_calories = 0
    total_cook_time = 0
    for day_menu in st.session_state.menu:
        for meal_type in ["breakfast", "lunch", "dinner"]:
            menu_name = day_menu[meal_type]
            if menu_name and menu_name in MENU_DETAILS:
                total_calories += MENU_DETAILS[menu_name]["calories"]
                total_cook_time += MENU_DETAILS[menu_name]["cook_time"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**1週間の総カロリー:** {total_calories}kcal")
        st.write(f"**1日平均カロリー:** {total_calories // 7}kcal")
    with col2:
        st.write(f"**1週間の総調理時間:** {total_cook_time}分")
        st.write(f"**1日平均調理時間:** {total_cook_time // 7}分")

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
        details = MENU_DETAILS[menu]
        st.write(f"**{menu}**: {', '.join(ingredients)} (カロリー: {details['calories']}kcal, 調理時間: {details['cook_time']}分, ジャンル: {details['genre']})")
