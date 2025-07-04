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

        出力形式は以下のようにしてください：

        [献立]
        - 月曜日：
          - 朝：〇〇
          - 昼：〇〇
          - 夜：〇〇
        （〜金曜、土曜、日曜も同様に）

        [買い物リスト]
        - 食材A：〇〇g
        - 食材B：〇〇個

        [レシピ]（以下は月曜日の料理の例です）
        ■料理名1
        材料：
        手順：

        ■料理名2...
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
            output = response.choices[0].message.content
        except Exception as e:
            st.error(f"献立の生成に失敗しました:{e}")
            st.stop()
        

        if output: 
            st.success("献立が完成しました！🎉")
            st.markdown("### 📝 献立と買い物リスト")
            st.markdown(output)
            meal_match = re.search(r"\[献立\](.*?)\[買い物リスト\]", output, re.DOTALL)
            shopping_match = re.search(r"\[買い物リスト\](.*?)\[レシピ\]", output, re.DOTALL)
            recipe_match = re.search(r"\[レシピ\](.*)", output, re.DOTALL)
            meal_plan_text = meal_match.group(1).strip() if meal_match else ""
            shopping_list_text = shopping_match.group(1).strip() if shopping_match else ""
            recipe_text = recipe_match.group(1).strip() if recipe_match else ""

        st.download_button(
        label="献立をテキストで保存",
        data=meal_plan_text.encode('utf-8'),
        file_name="weekly_meal_plan.txt",
        mime="text/plain"
        ) 
        st.download_button(
        label="買い物リストをテキストで保存",
        data=shopping_list_text.encode('utf-8'),
        file_name="shopping_list.txt",
        mime="text/plain"
        )
        st.download_button(
        label="レシピをテキストで保存",
        data=recipe_text.encode('utf-8'),   
        file_name="recipes.txt",
        mime="text/plain"
        )

            # --- レシピ取得機能 ---
        if output:
            matches = re.findall(r"[-・]\s*(朝|昼|夜|朝ごはん|昼食|夕食)[：:](.+)", output)
            meal_names = [name.strip() for _, name in matches]
            unique_meals = sorted(set(meal_names))

            st.markdown("### 🍳 レシピを見たい料理を選んでください")
            selected_meal = st.selectbox("料理を選択", [""] + unique_meals)

            if selected_meal:
                with st.spinner(f"{selected_meal} のレシピを作成中..."):
                    recipe_prompt = f"""
                    以下の料理のレシピを詳しく作成してください。

                    料理名: {selected_meal}

                    出力形式：
                    [材料]
                    - 食材A：量
                    - 食材B：量

                    [手順]
                    1. 手順1
                    2. 手順2
                    ...
                    """
                    try:
                        recipe_response = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "あなたは料理のレシピに詳しいプロのシェフです。"},
                            {"role": "user", "content": recipe_prompt}
                        ],
                        temperature=0.6
                        )
                        recipe_output = recipe_response.choices[0].message.content
                        st.markdown(f"### 📝 {selected_meal} のレシピ")
                        st.markdown(recipe_output)
                    except Exception as e:
                        st.error("レシピの生成に失敗しました。")
                        st.exception(e)
        else:
            st.error("献立の生成に失敗しました。")