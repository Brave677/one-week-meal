import streamlit as st
import openai

# Add custom CSS for overall UI design adjustments with light and dark mode support
st.markdown(
    """
    <style>
    .stApp {
        font-family: 'sans-serif';
    }
    
    /* Light mode */
    .light-mode {
        background-color: #ffffff;
        color: #333333;
    }
    .light-mode .stButton>button {
        background-color: #38a169;
        color: #ffffff;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        transition: background-color 0.3s ease;
    }
    .light-mode .stButton>button:hover {
        background-color: #2f855a;
    }
    .light-mode .stSidebar {
        background-color: #f7fafc;
    }
    .light-mode .stTable {
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Dark mode */
    .dark-mode {
        background-color: #1a202c;
        color: #e2e8f0;
    }
    .dark-mode .stButton>button {
        background-color: #2f855a;
        color: #e2e8f0;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        transition: background-color 0.3s ease;
    }
    .dark-mode .stButton>button:hover {
        background-color: #276749;
    }
    .dark-mode .stSidebar {
        background-color: #2d3748;
    }
    .dark-mode .stTable {
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Apply the mode class to the app
mode = st.sidebar.radio("モード選択", ("ライトモード", "ダークモード"))
mode_class = "light-mode" if mode == "ライトモード" else "dark-mode"
st.markdown(f'<div class="stApp {mode_class}">', unsafe_allow_html=True)

st.title("1週間の献立管理アプリ")

# OpenAI APIキーの入力
api_key = st.sidebar.text_input("OpenAI APIキー", type="password")

# 条件の入力
st.sidebar.header("献立の条件")
calorie_limit = st.sidebar.number_input("カロリー制限", min_value=0, value=2000)
allergies = st.sidebar.text_input("アレルギー", placeholder="例: 卵, 乳製品")

# 曜日リスト
DAYS = ["月", "火", "水", "木", "金", "土", "日"]

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

# OpenAIを使用して献立を生成する関数
if api_key:
    openai.api_key = api_key

    def generate_meal_plan(ingredients, calorie_limit, allergies):
        prompt = f"冷蔵庫の食材: {', '.join(ingredients)}\\nカロリー制限: {calorie_limit}kcal\\nアレルギー: {allergies}\\n1週間の献立を提案してください。"
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "献立を提案してください。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    # 献立生成ボタン
    if st.button("AIで献立を生成"):
        ingredients = list(st.session_state.fridge_ingredients.keys())
        meal_plan = generate_meal_plan(ingredients, calorie_limit, allergies)
        st.text_area("生成された献立", meal_plan, height=200)
else:
    st.warning("OpenAI APIキーを入力してください。")

# 献立の表示
st.header("1週間の献立一覧")
if "menu" in st.session_state:
    st.table(st.session_state.menu)
else:
    st.info("献立がまだ生成されていません。AIで生成してください。")

# Close the mode class div
st.markdown('</div>', unsafe_allow_html=True)