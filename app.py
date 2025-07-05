import streamlit as st
import openai
import re

# secrets.tomlファイルからAPIキーを取得
api_key = st.secrets["openai"]["api_key"]

# OpenAI APIに接続
openai.api_key = api_key

# カスタムCSS（Apple風：グリーン・オレンジ中心、清潔感のあるUI）
css = """
<style>
    /* ルート要素でカスタムプロパティを定義 */
    :root {
        /* ライトモードのデフォルト */
        --background-color: #ffffff;
        --text-color: #2d2d2d;
        --primary-color: #2f855a; /* グリーン */
        --secondary-background-color: #f0f0f0;
        --border-color: #dcdcdc;
        --shadow-color: rgba(0,0,0,0.05);
        --button-bg-color: #38a169; /* メイングリーン */
        --button-hover-bg-color: #2f855a;
        --download-button-bg-color: #ed8936; /* オレンジ */
    }

    /* ダークモードのカスタムプロパティ */
    [data-theme="dark"] {
        --background-color: #121212;  /* より黒に近い背景でコントラストUP */
        --text-color: #ffffff;        /* 真っ白な文字で読みやすく */
        --primary-color: #90ee90;     /* 明るめグリーン */
        --secondary-background-color: #1e1e1e;
        --border-color: #666666;
        --shadow-color: rgba(0, 0, 0, 0.3);
        --button-bg-color: #45c36f;   /* より明るく鮮やかに */
        --button-hover-bg-color: #34a95a;
        --download-button-bg-color: #ffa94d; /* 明るいオレンジで目立つ */
    }

    /* 全体の背景とフォント */
    body, .stApp {
        font-family: 'Segoe UI', sans-serif;
        padding: 1rem;
        box-sizing: border-box;
    }

    /* 見出し */
    .title {
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary-color);
        margin-bottom: 1rem;
    }

    /* 入力フォーム */
    textarea, input, .stSlider, {
       background-color: var(--secondary-background-color);
       color: var(--text-color);
       border: 1px solid var(--border-color);
       border-radius: 0.5rem;
       padding: 0.75rem;
       width: 100%;
       box-sizing: border-box;
    }

    .st-expander > summary {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-color);
        background-color: var(--secondary-background-color);
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
    }

    /* ボタン */
    div.stButton > button {
        background-color: var(--button-bg-color);
        color: white;
        padding: 0.6rem 1.2rem;
        font-size: 1rem;
        border-radius: 0.5rem;
        border: none;
        transition: 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: var(--button-hover-bg-color);
    }

    /* 出力コンテナ */
    .result-container {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border-radius: 0.75rem;
        box-shadow: 0 4px 8px var(--shadow-color);
        padding: 1.5rem;
        margin-top: 1rem;
    }

    /* ダウンロードボタン */
    .stDownloadButton > button {
        background-color: var(--download-button-bg-color);
        color: white;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        border-radius: 0.5rem;
        border: none;
    }

    /* フォーカススタイル */
    textarea:focus, input:focus {
        outline: none;
        box-shadow: 0 0 0 3px var(--primary-color);
    }

    /* レスポンシブ対応（スマホ・タブレット） */
    @media screen and (max-width: 768px) {
        body, .stApp {
            padding: 0.5rem !important;
        }

        .title {
            font-size: 1.5rem !important;
        }

        .st-expander > summary {
            font-size: 1rem !important;
        }

        div.stButton > button, .stDownloadButton > button {
            width: 100%;
            font-size: 1rem !important;
        }

        textarea, input {
            font-size: 1rem !important;
        }

        .result-container {
            padding: 1rem !important;
        }
    }

</style>
"""
st.markdown(css, unsafe_allow_html=True) 


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

# --- 再生成ボタン ---
regenerate = st.button("🎲 献立を再生成する")

# --- 献立生成処理 ---
if submit or regenerate:  
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

        【火曜日】
        ■朝：料理名
        [材料]
        - 食材：量
        [手順]
        1. 手順...

        【火曜日】...【日曜日】まで必ず含めてください。
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
    st.success("献立が完成しました！🎉")
    tabs = st.tabs(["📅 献立", "🛒 買い物リスト", "📖 レシピ"])
    # 正規表現で各セクションを抽出
    meal_match = re.search(r"\[献立\]([\s\S]*?)(?:\[買い物リスト\]|$)", output)
    shopping_match = re.search(r"\[買い物リスト\]([\s\S]*?)\[レシピ\]", output)
    recipe_match = re.search(r"\[レシピ\]([\s\S]*)", output)

    meal_plan_text = meal_match.group(1).strip() if meal_match else ""
    shopping_list_text = shopping_match.group(1).strip() if shopping_match else ""
    recipe_text = recipe_match.group(1).strip() if recipe_match else ""

    with tabs[0]:
        st.markdown("### 📅 献立プラン")
        st.markdown(meal_plan_text)
        st.download_button("📥 献立をテキストで保存", meal_plan_text.encode("utf-8"), "weekly_meal_plan.txt")

    with tabs[1]:
        st.markdown("### 🛒 買い物リスト")
        st.markdown(shopping_list_text)
        st.download_button("📥 買い物リストをテキストで保存", shopping_list_text.encode("utf-8"), "shopping_list.txt")
    
    with tabs[2]:
        st.markdown("### 📖 レシピ")
        if recipe_text:
            daily_recipes = re.findall(
                r"【(月曜日|火曜日|水曜日|木曜日|金曜日|土曜日|日曜日)】\s*([\s\S]*?)(?=(?:【(?:月曜日|火曜日|水曜日|木曜日|金曜日|土曜日|日曜日)】)|\Z)",
                recipe_text
            )
            daily_recipes_dict = {day: content.strip() for day, content in daily_recipes}

            ordered_days = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
            for day in ordered_days:
                if day in daily_recipes_dict:
                    content = daily_recipes_dict[day]
                    with st.expander(f"✨ **{day}のレシピ**"):
                        st.markdown(content)
                        st.download_button(
                            f"📥 {day}のレシピをテキストで保存",
                            content.encode("utf-8"),
                            f"{day}_recipe.txt"
                        )
                else:
                    with st.expander(f"⚠️ **{day}のレシピ（未出力）**"):
                        st.warning(f"{day}のレシピがAI出力に含まれていませんでした。再生成をお試しください。")
        else:
            st.warning("レシピが見つかりませんでした。")