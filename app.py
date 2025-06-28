import streamlit as st
import openai

# OpenAI APIキー設定
api_key = st.sidebar.text_input("OpenAI APIキー", type="password")

# --- UI: ユーザー入力 ---
st.title("1週間の献立AIアプリ 🍽️")

with st.form("meal_form"):
    st.subheader("条件を入力してください")
    available_ingredients = st.text_area("冷蔵庫にある食材（カンマ区切り）")
    preferences = st.text_input("好み（例：和食中心、低糖質、ボリューム重視など）")
    budget = st.slider("1週間の予算（円）", 1000, 20000, 5000)
    submit = st.form_submit_button("献立を作成する")

if submit:
    with st.spinner("AIが献立を考え中...⏳"):
        prompt = f"""
        以下の条件に基づいて、1週間分（7日分×朝昼晩）の献立を作成してください。
        また、それに基づく買い物リスト（食材と必要量）も出力してください。

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
        """

        response = openai.chat.completions.create(
            model="gpt-4o",  # または "gpt-4"
            messages=[
                {"role": "system", "content": "あなたは献立を考えるプロの料理アドバイザーです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        output = response.choices[0].message.content
        st.success("献立が完成しました！🎉")
        st.markdown(output)

        # ダウンロードリンク
    