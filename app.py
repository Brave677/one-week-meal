import streamlit as st
import openai
import re

# secrets.tomlファイルからAPIキーを取得
api_key = st.secrets["openai"]["api_key"]

# OpenAI APIに接続
openai.api_key = api_key

# カスタムCSS（Apple風：グリーン・オレンジ中心、清潔感のあるUI）
st.markdown("""
<style>
    /* 全体の背景とフォント */
    body, .stApp {
        background-color: var(--background-color, #ffffff);
        color: var(--text-color, #2d2d2d);
        font-family: 'Segoe UI', sans-serif;
        padding: 1rem;
    }

    /* 見出し */
    .title {
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary-color, #2f855a);  /* グリーン */
        margin-bottom: 1rem;
    }

    /* 入力フォーム */
    textarea, input, .stSlider {
       background-color: var(--secondary-background-color, #f0f0f0);
       color: var(--text-color, #2d2d2d);
       border: 1px solid #dcdcdc;
       border-radius: 0.5rem;
       padding: 0.75rem;
    }
    .st-expander > summary {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-color, #2d2d2d);
    background-color: var(--secondary-background-color, #f0f0f0);
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border: 1px solid #ccc;
}

    /* ボタン */
    div.stButton > button {
        background-color: #38a169; /* メイングリーン */
        color: white;
        padding: 0.6rem 1.2rem;
        font-size: 1rem;
        border-radius: 0.5rem;
        border: none;
        transition: 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #2f855a;
    }

    /* 出力コンテナ */
    .result-container {
        background-color: var(--secondary-background-color, #f0f0f0);
        color: var(--text-color, #2d2d2d);
        border-radius: 0.75rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        padding: 1.5rem;
        margin-top: 1rem;
    }

    /* ダウンロードボタン */
    .stDownloadButton > button {
        background-color: #ed8936; /* オレンジ */
        color: white;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        border-radius: 0.5rem;
        border: none;
    }

    /* フォーカススタイル */
    textarea:focus, input:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(72,187,120,0.5); /* ライトグリーンのリング */
    }
</style>
""", unsafe_allow_html=True)

# --- UI: ユーザー入力 ---
st.title("One-week-meal 🍽️")
st.markdown("""
このアプリでは、以下のことができます：
- 冷蔵庫の食材・好み・予算をもとに1週間の献立を自動提案
- 献立に必要な買い物リストを作成
- 各料理のレシピを個別に生成
- テキストで献立・買い物リスト・レシピを保存
""")
with st.expander("🍳 **条件を入力する**（食材・好み・予算）", expanded=True):
    with st.form("meal_form"):
        st.subheader("条件を入力してください")
        available_ingredients = st.text_area("冷蔵庫にある食材（カンマ区切り）", placeholder="例：キャベツ、鶏むね肉、卵、豆腐")
        preferences = st.text_input("好み（例：和食中心、低糖質、ボリューム重視など）", placeholder="和食中心、ボリューム重視など")
        budget = st.slider("1週間の予算（円）", 1000, 20000, 5000, step=500)
        submit = st.form_submit_button("献立を作成する")

if submit:
    with st.spinner("AIが献立を考え中...⏳"):
        prompt = f"""
        以下の条件に基づいて、1週間分（7日分×朝昼晩）の献立を作成してください。
        また、それに基づく買い物リスト（食材と必要量）と、各料理のレシピ詳細（材料・手順）も出力してください。


        [条件]
        - 冷蔵庫にある食材: {available_ingredients}
        - ユーザーの好み: {preferences}
        - 1週間の予算: {budget}円
        - 栄養バランスを考慮し、食材をなるべく無駄にしないこと
        - 各料理は1食あたり600kcal以下、調理時間は30分以内とすること

        出力形式は以下のようにしてください：

        [献立]
        - 月曜日：
          - 朝：料理名
          - 昼：料理名
          - 夜：料理名
        （〜日曜日まで同様に）

       [買い物リスト]
        - 食材A：〇〇g
        - 食材B：〇〇個

        [レシピ]
        各曜日の料理ごとに以下の形式で出力してください：

        【月曜日】
        ■朝：料理名
        [材料]
        - 食材：量
        [手順]
        1. 手順...

        ■昼：料理名
        ...

        【火曜日】
        ...
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",  # または "gpt-4"
                messages=[
                {"role": "system", "content": "あなたは献立を考えるプロの料理アドバイザーです。"},
                {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            st.session_state["output"] = response.choices[0].message.content
        except Exception as e:
            st.error("OpenAI APIのエラーが発生しました。")
            st.exception(e) 
            st.stop()
        
# outputが存在する場合のみ、以下のUIを表示
if "output" in st.session_state:
    output = st.session_state["output"]

    # 正規表現で各セクションを抽出
    meal_match = re.search(r"\[献立\](.*?)\[買い物リスト\]", output, re.DOTALL)
    shopping_match = re.search(r"\[買い物リスト\](.*?)\[レシピ\]", output, re.DOTALL)
    recipe_match = re.search(r"\[レシピ\](.*)", output, re.DOTALL)

    meal_plan_text = meal_match.group(1).strip() if meal_match else ""
    shopping_list_text = shopping_match.group(1).strip() if shopping_match else ""
    recipe_text = recipe_match.group(1).strip() if recipe_match else ""

    tabs = st.tabs(["📅 献立", "🛒 買い物リスト", "📖 レシピ"])

    with tabs[0]:
        st.markdown("### 📅 献立プラン")
        if meal_plan_text:
            st.markdown(meal_plan_text)
            st.download_button(
                label="📥 献立をテキストで保存",
                data=meal_plan_text.encode('utf-8'),
                file_name="weekly_meal_plan.txt",
                mime="text/plain"
            )
        else:
            st.info("献立データがありません。")

    with tabs[1]:
        st.markdown("### 🛒 買い物リスト")
        if shopping_list_text:
            st.markdown(shopping_list_text)
            st.download_button(
                label="📥 買い物リストをテキストで保存",
                data=shopping_list_text.encode('utf-8'),
                file_name="shopping_list.txt",
                mime="text/plain"
            )
        else:
            st.info("買い物リストデータがありません。")

    with tabs[2]:
        st.markdown("### 📖 レシピ一覧")
        if recipe_text:
            # 各レシピブロックを整形して表示
            for block in recipe_text.split("■"):
                if block.strip():
                    # 各レシピの最初の行をタイトルとして抽出
                    first_line = block.strip().split('\n')[0]
                    st.markdown(f"<div class='recipe-card'>**{first_line}**<br>{block.strip().replace(first_line, '', 1)}</div>", unsafe_allow_html=True)
            st.download_button(
                label="📥 レシピをテキストで保存",
                data=recipe_text.encode('utf-8'),
                file_name="all_recipes.txt",
                mime="text/plain"
            )
        else:
            st.info("レシピデータがありません。")

  