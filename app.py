import streamlit as st
import openai

# OpenAI APIキー設定
api_key = st.sidebar.text_input("OpenAI APIキー", type="password")

if not api_key:
    st.error("OPENAI APIキーを入力してください")
    st.stop()
openai.api_key = api_key

# カスタムCSS（Apple風：グリーン・オレンジ中心、清潔感のあるUI）
st.markdown("""
<style>
    /* 全体の背景とフォント */
    body, .stApp {
        background-color: #ffffff;
        color: #2d2d2d;
        font-family: 'Segoe UI', sans-serif;
        padding: 1rem;
    }

    /* 見出し */
    .title {
        font-size: 2rem;
        font-weight: bold;
        color: #2f855a;  /* グリーン */
        margin-bottom: 1rem;
    }

    /* 入力フォーム */
    textarea, input, .stSlider {
        background-color: #f7f7f7;
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
        background-color: white;
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
            st.download_button(
            label="献立をテキストで保存",
            data=output.encode('utf-8'),
            file_name="weekly_meal_plan.txt",
            mime="text/plain"
            )
        else:
            st.error("献立の生成に失敗しました。API応答を確認してください。")
            st.write(response)  # デバッグ用