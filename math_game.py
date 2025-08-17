import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
# インポート文を修正
from config import (GAME_SETTINGS, DIFFICULTY_SETTINGS, SCORE_SETTINGS, 
                   USERS, DEFAULT_USER, SOUND_EFFECTS, SCORES_FILE, 
                   DATA_DIR, HISTORY_MAX_MISTAKES, SOUND_DIR, SOUND_FILES)

# 日本語フォント設定
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

# ページ設定
st.set_page_config(
    page_title="目指せ！計算王",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSSスタイル（ボタンを大きく）
st.markdown("""
<style>
    .main-title {
        font-size: clamp(28px, 8vw, 42px);
        font-weight: bold;
        color: #FF5733;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 24px;
        color: #333;
        text-align: center;
        margin-bottom: 20px;
    }
    .question {
        font-size: clamp(32px, 10vw, 40px);
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin: 30px 0;
    }
    .correct {
        font-size: 22px;
        color: #4CAF50;
        text-align: center;
        padding: 10px;
        background-color: rgba(76, 175, 80, 0.1);
        border-radius: 8px;
        margin: 10px 0;
    }
    .incorrect {
        font-size: 22px;
        color: #F44336;
        text-align: center;
        padding: 10px;
        background-color: rgba(244, 67, 54, 0.1);
        border-radius: 8px;
        margin: 10px 0;
    }
    .score-display {
        font-size: 26px;
        font-weight: bold;
        color: #673AB7;
        text-align: center;
    }
    .time-display {
        font-size: 22px;
        color: #FF9800;
        text-align: center;
    }
    .result-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 20px 0;
    }
    .score-card {
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
    }
    .progress-container {
        margin: 10px 0;
    }
    .answer-display {
        font-size: 36px;
        font-weight: bold;
        color: #1976D2;
        text-align: center;
        background-color: #E3F2FD;
        border: 3px solid #1976D2;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    /* ボタンサイズ拡大 */
    button {
        font-size: 28px !important;
        padding: 20px !important;
        min-height: 80px !important;
    }
    /* 問題交互の背景色 */
    .question-even {
        background-color: #f9f9ff;
        padding: 20px;
        border-radius: 10px;
    }
    .question-odd {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
    }
    /* 効果音用の非表示要素 */
    .sound-element {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# 効果音用のHTML要素（修正版）
st.markdown("""
<audio id="correct-sound" preload="auto" controls style="display:none;">
    <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLHPH7tiJNwgZVrPn4aRNGRFCltDq0mc0KDpqrN/lu2kpLxlQnN/z33VDQSJR4+9OIQw5rNyxOA1l3tKiVXGy2fWdRDyywPehQumm0eC7Z7Ka6d+8eCK+sf7qtbf9Ac++SQHEpOj7yc5GFMCgGPG/wrzt1UTLpT70s8fAb0W7sjTls83dy7qtoH8wp+yhuQALtZf0xrBE+bqhntX/4+bbyd+hkLPWztDr6NapjNfGt9W8n+zmtLjisKqV3MKwluPas6/C4bOj6cSsi+C0tZbE+OJ3SjoAAAAAAAAAAAA=" type="audio/wav">
    効果音の再生ができません
</audio>

<audio id="incorrect-sound" preload="auto" controls style="display:none;">
    <source src="data:audio/wav;base64,UklGRpYDAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YXIDAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLHPH7tiJNwgZVrPn4aRNGRFCltDq0mc0KDpqrN/lu2kpLxlQnNLL0j8sNFB72Ml7KhgC68DX9t3O6+Xm7/vw3LS4xtDLu7O/2ufox66+1dje0ru5yOPx5Mq2veHe18vCt77k7uPOuLnh6OPVvcG6volIAAAAAAAAAAAA" type="audio/wav">
    効果音の再生ができません
</audio>

<script>
// 効果音の事前ロード確認
document.addEventListener('DOMContentLoaded', function() {
    console.log('効果音の初期化');
    const correctSound = document.getElementById('correct-sound');
    const incorrectSound = document.getElementById('incorrect-sound');
    
    if (correctSound) console.log('正解効果音: 読み込み済み');
    if (incorrectSound) console.log('不正解効果音: 読み込み済み');
    
    // iOS/Safari対策: ユーザー操作に応答するためのダミー再生
    document.body.addEventListener('click', function() {
        const silent = new Audio("data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==");
        silent.volume = 0.01;
        silent.play().then(() => {
            console.log("オーディオ再生許可取得");
        }).catch(e => {
            console.log("オーディオ許可エラー:", e);
        });
    }, {once: true});
});
</script>
""", unsafe_allow_html=True)

# リアルタイム時間更新用JavaScript（エラー修正：変数を直接展開）
st.markdown("""
<script>
    function updateTimer() {
        const startTime = window.streamlitStartTime || Date.now() / 1000;
        const timerElement = document.getElementById('realtime-timer');
        if (!timerElement) return;
        
        setInterval(() => {
            const currentTime = Date.now() / 1000;
            const elapsedTime = Math.floor(currentTime - startTime);
            const minutes = Math.floor(elapsedTime / 60);
            const seconds = elapsedTime % 60;
            timerElement.innerText = `時間: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }
    
    if (document.readyState === 'complete') {
        updateTimer();
    } else {
        window.addEventListener('load', updateTimer);
    }
</script>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None
if 'game_complete' not in st.session_state:
    st.session_state.game_complete = False
if 'results' not in st.session_state:
    st.session_state.results = []
if 'current_answer' not in st.session_state:
    st.session_state.current_answer = ""
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = "イージー"
if 'mode' not in st.session_state:
    st.session_state.mode = "足し算"
# 新しいセッション状態
if 'last_result_message' not in st.session_state:
    st.session_state.last_result_message = {"text": "", "type": ""}
if 'current_user' not in st.session_state:
    st.session_state.current_user = DEFAULT_USER
if 'question_parity' not in st.session_state:  # 問題の偶数/奇数判定用
    st.session_state.question_parity = 0

# ユーザーデータの読み込み・保存関数
def load_scores():
    try:
        if SCORES_FILE.exists():
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                scores = json.load(f)
                
                # データ構造の移行処理
                # 古い形式（リスト）から新しい形式（辞書）への変換
                for user_id, user_data in scores.items():
                    if isinstance(user_data, list):
                        # 古い形式のデータを検出
                        scores[user_id] = {
                            "history": user_data,  # 古いスコア履歴を history キーに移動
                            "mistakes": []  # 新しい mistakes キーを追加
                        }
                
                # 変換したデータを保存
                try:
                    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
                        json.dump(scores, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    st.warning(f"データ変換中のエラー: {e}")
                    
                return scores
        return {}
    except Exception as e:
        st.warning(f"スコアデータの読み込みエラー: {e}")
        return {}

# デバッグ用の関数
def debug_file_system():
    """ファイルシステムの状態をデバッグ出力する"""
    import os  # 関数内でインポート
    debug_info = {
        "current_dir": os.getcwd(),
        "data_dir_exists": os.path.exists(DATA_DIR),
        "data_dir_path": str(DATA_DIR.absolute()),
        "scores_file_exists": os.path.exists(SCORES_FILE),
        "scores_file_path": str(SCORES_FILE.absolute()),
    }
    
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                file_content = f.read()
                debug_info["file_size"] = len(file_content)
                debug_info["file_content_preview"] = file_content[:100] if file_content else "空ファイル"
        except Exception as e:
            debug_info["file_read_error"] = str(e)
    
    return debug_info

# スコア保存関数の修正 - 間違えた問題の履歴を追加
def save_score(user_id, mode, difficulty, score, correct_count, total_time, results):
    """スコアを保存する関数（完全修正版）"""
    try:
        import os
        import json
        import shutil
        from datetime import datetime
        
        # デバッグ情報を表示
        debug_info = debug_file_system()
        print(f"保存開始: {debug_info}")
        
        # ディレクトリを確実に作成
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 既存データの読み込み
        scores = {}
        if os.path.exists(SCORES_FILE):
            try:
                with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                    scores = json.load(f)
            except Exception as e:
                print(f"既存スコアの読み込みエラー: {e}")
                scores = {}
        
        # ユーザーデータの初期化
        if user_id not in scores:
            scores[user_id] = {
                "history": [],
                "mistakes": []
            }
        elif not isinstance(scores[user_id], dict):
            # 古い形式のデータを変換
            scores[user_id] = {
                "history": scores[user_id] if isinstance(scores[user_id], list) else [],
                "mistakes": []
            }
        
        # スコア履歴に追加
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_history = {
            "timestamp": timestamp,
            "mode": mode,
            "difficulty": difficulty,
            "score": score,
            "correct_count": correct_count,
            "total_questions": GAME_SETTINGS["total_questions"],
            "total_time": total_time
        }
        scores[user_id]["history"].append(new_history)
        print(f"履歴データを追加: {new_history}")
        
        # 間違えた問題の履歴を更新
        mistakes = [
            {
                "timestamp": timestamp,
                "problem": r["問題"],
                "correct_answer": r["正解"],
                "user_answer": r["回答"],
                "mode": mode,
                "difficulty": difficulty
            }
            for r in results if r["正誤"] == "×"
        ]
        
        # 既存のミスと新しいミスを結合
        if "mistakes" in scores[user_id]:
            all_mistakes = mistakes + scores[user_id]["mistakes"]
        else:
            all_mistakes = mistakes
            
        # 最新のものから指定数だけ保持
        scores[user_id]["mistakes"] = all_mistakes[:HISTORY_MAX_MISTAKES]
        
        # 確実な方法でファイルに保存
        try:
            temp_file = str(SCORES_FILE) + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
            
            # 一時ファイルが正常に書き込めたら、本来のファイルに移動
            shutil.move(temp_file, SCORES_FILE)
            
            print(f"スコア保存成功: {SCORES_FILE}")
            return True
        except Exception as e:
            import traceback
            print(f"保存エラー: {e}")
            print(traceback.format_exc())
            return False
            
    except Exception as e:
        import traceback
        print(f"スコア保存処理エラー: {e}")
        print(traceback.format_exc())
        return False

def generate_question(mode, difficulty):
    """問題を生成する関数"""
    try:
        if mode == "足し算":
            if difficulty == "イージー":
                # 答えが一桁の足し算
                answer = random.randint(0, 9)
                a = random.randint(0, answer)
                b = answer - a
                return a, b, a + b, "+"
            elif difficulty == "ノーマル":
                # 一桁同士の足し算
                a = random.randint(0, 9)
                b = random.randint(0, 9)
                return a, b, a + b, "+"
            else:  # ハード
                # 二桁同士の足し算
                a = random.randint(10, 99)
                b = random.randint(10, 99)
                return a, b, a + b, "+"
        
        elif mode == "引き算":
            if difficulty == "イージー":
                # 一桁同士の引き算
                a = random.randint(0, 9)
                b = random.randint(0, a)  # bはa以下（マイナスを避けるため）
                return a, b, a - b, "-"
            elif difficulty == "ノーマル":
                # 二桁同士の引き算（繰り下がりなし）
                tens_a = random.randint(1, 9)
                ones_a = random.randint(0, 9)
                tens_b = random.randint(0, tens_a)
                ones_b = random.randint(0, ones_a)
                a = tens_a * 10 + ones_a
                b = tens_b * 10 + ones_b
                return a, b, a - b, "-"
            else:  # ハード
                # 二桁同士の引き算（繰り下がりあり）
                a = random.randint(10, 99)
                b = random.randint(1, a)  # bはa以下かつ0より大きい
                return a, b, a - b, "-"
        
        else:  # 掛け算
            if difficulty == "イージー":
                # 0～5の段の九九
                a = random.randint(0, 5)
                b = random.randint(0, 5)
                return a, b, a * b, "×"
            elif difficulty == "ノーマル":
                # 0～9の段の九九
                a = random.randint(0, 9)
                b = random.randint(0, 9)
                return a, b, a * b, "×"
            else:  # ハード
                # 0～15の段の九九 (エラー修正)
                a = random.randint(0, 15)
                b = random.randint(0, 15)
                return a, b, a * b, "×"
    except Exception as e:
        st.error(f"問題生成エラー: {e}")
        # エラー時のフォールバック問題
        return 1, 1, 2, "+"

def calculate_score(answer_time, is_correct, difficulty):
    """
    回答時間と正誤に基づいてスコアを計算する
    難易度に応じたスコア係数も適用する
    """
    score_multiplier = DIFFICULTY_SETTINGS[difficulty]["score_multiplier"]
    
    if is_correct:
        # 正解の場合、時間に応じてボーナス
        thresholds = SCORE_SETTINGS["time_thresholds"]
        if answer_time <= thresholds["fast"]:
            return SCORE_SETTINGS["time_bonus"]["fast"] * score_multiplier
        elif answer_time <= thresholds["medium"]:
            return SCORE_SETTINGS["time_bonus"]["medium"] * score_multiplier
        elif answer_time <= thresholds["slow"]:
            return SCORE_SETTINGS["time_bonus"]["slow"] * score_multiplier
        else:
            return SCORE_SETTINGS["time_bonus"]["very_slow"] * score_multiplier
    else:
        # 不正解の場合、ペナルティ（難易度によらず一定）
        return SCORE_SETTINGS["incorrect_penalty"]

def reset_game():
    st.session_state.game_started = False
    st.session_state.current_question = None
    st.session_state.question_count = 0
    st.session_state.score = 0
    st.session_state.start_time = None
    st.session_state.question_start_time = None
    st.session_state.game_complete = False
    st.session_state.results = []
    st.session_state.current_answer = ""
    st.session_state.last_result_message = {"text": "", "type": ""}
    st.session_state.question_parity = 0

def add_digit(digit):
    if len(st.session_state.current_answer) < GAME_SETTINGS["max_answer_digits"]:
        st.session_state.current_answer += str(digit)

def clear_answer():
    st.session_state.current_answer = ""

def backspace():
    if st.session_state.current_answer:
        st.session_state.current_answer = st.session_state.current_answer[:-1]

# Base64エンコードした効果音を直接埋め込む
def play_sound(sound_type):
    """効果音を鳴らすJavaScriptを実行する（改良版）"""
    if sound_type == "correct":
        base64_data = SOUND_EFFECTS["correct"]
    elif sound_type == "incorrect":
        base64_data = SOUND_EFFECTS["incorrect"]
    else:
        return
    
    # JavaScriptコードを生成（インライン再生方式）
    js_code = f"""
    <script>
        (function() {{
            console.log("効果音再生: {sound_type}");
            
            // 新しいAudio要素を作成（毎回新しく作ることで再生の問題を回避）
            const audio = new Audio("{base64_data}");
            audio.volume = 0.5;
            
            // ユーザー操作として再生を試みる（ボタンクリックの延長として）
            setTimeout(function() {{
                audio.play().then(() => {{
                    console.log("効果音再生成功");
                }}).catch(error => {{
                    console.error("効果音再生エラー:", error);
                    // 再生が失敗した場合は、別の方法を試みる
                    const backupAudio = document.createElement('audio');
                    backupAudio.src = "{base64_data}";
                    document.body.appendChild(backupAudio);
                    backupAudio.play();
                    setTimeout(() => document.body.removeChild(backupAudio), 1000);
                }});
            }}, 100);
        }})();
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

def play_sound_old(sound_type):
    """効果音を鳴らす（ローカルファイル版）"""
    try:
        sound_file = SOUND_FILES.get(sound_type)
        if not sound_file:
            print(f"未定義の効果音タイプ: {sound_type}")
            return
            
        sound_path = str(SOUND_DIR / sound_file)
        
        # ファイルの存在を確認
        if not os.path.exists(SOUND_DIR / sound_file):
            print(f"効果音ファイルが見つかりません: {sound_file} (パス: {sound_path})")
            return
            
        # JavaScriptで効果音を再生
        js_code = f"""
        <script>
            (function() {{
                console.log("効果音再生: {sound_type} ({sound_path})");
                const audio = new Audio("{sound_path.replace('\\\\', '/')}");
                audio.volume = 0.5;
                
                // 再生を試みる
                const playPromise = audio.play();
                
                // 再生が成功したか確認
                if (playPromise !== undefined) {{
                    playPromise.then(() => {{
                        console.log("効果音再生成功");
                    }}).catch(error => {{
                        console.error("効果音再生エラー:", error);
                    }});
                }}
            }})();
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
    except Exception as e:
        print(f"効果音再生中にエラーが発生しました: {e}")

def main():
    st.markdown('<div class="main-title">🧮 目指せ！計算王 🧮</div>', unsafe_allow_html=True)
    
    # CSS追加：ユーザー選択ボタンのカスタムスタイルと見出しの改善
    st.markdown("""
    <style>
    /* 見出しのスタイル改善 */
    .section-heading {
        font-size: 20px;
        color: #FFFFFF;  /* 白 */
        font-weight: bold;
        text-align: center;
        margin-bottom: 25px;
        padding: 10px;
        background: linear-gradient(to right, rgba(21, 101, 192, 0.1), rgba(21, 101, 192, 0.2), rgba(21, 101, 192, 0.1));
        border-radius: 8px;
    }
    
    /* ユーザーボタンのスタイル */
    .user-button-selected {
        background-color: #1976D2;
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #0d47a1;
        margin-bottom: 15px;
    }
    .user-button-normal {
        background-color: #f5f5f5;
        color: #333;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #ddd;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 効果音ファイルの確認
    missing_sounds = []
    for sound_type, filename in SOUND_FILES.items():
        sound_path = SOUND_DIR / filename
        if not os.path.exists(sound_path):
            missing_sounds.append(f"{filename} (パス: {sound_path})")
    
    if missing_sounds:
        st.warning(f"""
        ⚠️ 効果音ファイルが見つかりません:
        {', '.join(missing_sounds)}
        
        「{SOUND_DIR}」フォルダに効果音ファイルを配置してください。
        効果音なしでもゲームは動作します。
        """)

    # サイドバーにユーザーの履歴表示
    with st.sidebar:
        st.title("スコア履歴")
        
        # ユーザー選択（サイドバー用）
        user_options = {uid: f"{data['avatar']} {data['name']}" for uid, data in USERS.items()}
        selected_user = st.selectbox(
            "ユーザーを選択", 
            options=list(user_options.keys()),
            format_func=lambda x: user_options[x],
            index=list(user_options.keys()).index(st.session_state.current_user),
            key="sidebar_user"
        )
        
        # 履歴を表示
        scores = load_scores()
        if selected_user in scores:
            user_data = scores[selected_user]
            
            # データ形式を確認
            if isinstance(user_data, list):
                # 古い形式のデータ
                history = user_data
                mistakes = []
            else:
                # 新しい形式のデータ
                history = user_data.get("history", [])
                mistakes = user_data.get("mistakes", [])
            
            # スコア履歴の表示
            if history:
                st.subheader("📊 スコア履歴")
                df = pd.DataFrame(history)
                df["日時"] = df["timestamp"]
                df["モード"] = df["mode"] + " (" + df["difficulty"] + ")"
                df["スコア"] = df["score"]
                df["正解数"] = df["correct_count"]
                
                st.dataframe(
                    df[["日時", "モード", "スコア", "正解数"]].sort_values("日時", ascending=False),
                    hide_index=True,
                    use_container_width=True
                )
            
            # 間違えた問題の履歴
            if mistakes:
                st.subheader("🔍 苦手な問題")
                mistake_df = pd.DataFrame(mistakes)
                mistake_df["日時"] = mistake_df["timestamp"]
                mistake_df["問題"] = mistake_df["problem"]
                mistake_df["正解"] = mistake_df["correct_answer"]
                mistake_df["回答"] = mistake_df["user_answer"]
                mistake_df["モード"] = mistake_df["mode"] + " (" + mistake_df["difficulty"] + ")"
                
                st.dataframe(
                    mistake_df[["日時", "問題", "正解", "回答", "モード"]].sort_values("日時", ascending=False).head(10),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("間違えた問題の履歴はありません")
            
            # 履歴削除ボタン
            if history or mistakes:
                if st.button("履歴を削除", key="delete_history"):
                    scores[selected_user] = {"history": [], "mistakes": []}
                    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
                        json.dump(scores, f, ensure_ascii=False, indent=2)
                    st.success("履歴を削除しました")
                    st.rerun()
        else:
            st.info("まだスコア履歴がありません")
    
    # ゲーム開始前の画面
    if not st.session_state.game_started and not st.session_state.game_complete:
        # ユーザー選択UIの改善（ゲーム開始前画面）
        st.markdown('<div class="section-heading">👤 プレイヤーを選んでね！</div>', unsafe_allow_html=True)
        
        # ユーザー選択のグリッド表示
        cols = st.columns(len(USERS))
        for i, (uid, user_data) in enumerate(USERS.items()):
            with cols[i]:
                user_selected = st.session_state.current_user == uid
                
                # 選択状態に応じたクラス
                button_class = "user-button-selected" if user_selected else "user-button-normal"
                
                if user_selected:
                    # 選択済みのユーザー表示
                    st.markdown(f"""
                    <div class="{button_class}">
                        <div style="font-size: 40px;">{user_data['avatar']}</div>
                        <div style="font-size: 18px; font-weight: bold;">
                            {user_data['name']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 非選択ユーザー（ボタン）
                    if st.button(
                        f"{user_data['avatar']}\n{user_data['name']}",
                        key=f"user-{uid}",
                        use_container_width=True
                    ):
                        st.session_state.current_user = uid
                        st.rerun()
        
        # モードと難易度の選択
        st.markdown('<div class="section-heading">🎮 ゲームモードを選んでね！</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            mode = st.selectbox("計算の種類", ["足し算", "引き算", "掛け算"], index=0)
        with col2:
            difficulty = st.selectbox("むずかしさ", ["イージー", "ノーマル", "ハード"], index=0)
        
        # モード説明
        multiplier = DIFFICULTY_SETTINGS[difficulty]["score_multiplier"]
        thresholds = SCORE_SETTINGS["time_thresholds"]
        st.info(f"""
        **{mode}（{difficulty}）のルール**
        
        {DIFFICULTY_SETTINGS[difficulty][mode]}
        
        **スコア計算：**
        - {thresholds["fast"]}秒以内に正解：{SCORE_SETTINGS["time_bonus"]["fast"] * multiplier}点
        - {thresholds["medium"]}秒以内に正解：{SCORE_SETTINGS["time_bonus"]["medium"] * multiplier}点
        - {thresholds["slow"]}秒以内に正解：{SCORE_SETTINGS["time_bonus"]["slow"] * multiplier}点
        - それ以上の時間で正解：{SCORE_SETTINGS["time_bonus"]["very_slow"] * multiplier}点
        - 間違えた場合：{SCORE_SETTINGS["incorrect_penalty"]}点
        
        全部で{GAME_SETTINGS["total_questions"]}問あるよ！がんばって！
        """)
        
        # スタートボタン
        if st.button("ゲームスタート！", use_container_width=True):
            st.session_state.game_started = True
            st.session_state.mode = mode
            st.session_state.difficulty = difficulty
            st.session_state.start_time = time.time()
            st.session_state.question_count = 0
            st.session_state.score = 0
            st.session_state.results = []
            
            # 問題生成を確実に行う
            try:
                st.session_state.current_question = generate_question(mode, difficulty)
                if not st.session_state.current_question:
                    raise ValueError("問題が生成されませんでした")
            except Exception as e:
                st.error(f"初期問題生成エラー: {e}")
                # フォールバック問題を設定
                st.session_state.current_question = (1, 1, 2, "+")
            
            st.session_state.question_start_time = time.time()
            st.session_state.question_parity = 0
            st.rerun()
    
    elif st.session_state.game_started and not st.session_state.game_complete:
        # 問題が正しく生成されているか確認
        if not st.session_state.current_question:
            st.error("問題の生成に問題が発生しました。ゲームをリセットします。")
            reset_game()
            st.rerun()
            
        # リアルタイム経過時間表示（JavaScript経由で更新）
        st.markdown(f'<div id="realtime-timer" class="time-display">時間: 0:00</div>', unsafe_allow_html=True)
        # JavaScriptでタイマー開始時刻を設定
        st.markdown(f"""
        <script>
            window.streamlitStartTime = {st.session_state.start_time};
        </script>
        """, unsafe_allow_html=True)
        
        # 前回の結果メッセージ表示（継続表示）
        if st.session_state.last_result_message["text"]:
            message_type = st.session_state.last_result_message["type"]
            message_text = st.session_state.last_result_message["text"]
            st.markdown(f'<div class="{message_type}">{message_text}</div>', unsafe_allow_html=True)
        
        # 進捗バーの表示
        progress = st.session_state.question_count / GAME_SETTINGS["total_questions"]
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.progress(progress)
        st.markdown(f'<div style="text-align: center;">問題 {st.session_state.question_count} / {GAME_SETTINGS["total_questions"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # スコア表示
        st.markdown(f'<div class="score-display">スコア: {st.session_state.score}</div>', unsafe_allow_html=True)
        
        # 問題表示（背景色を交互に変える）
        a, b, correct_answer, symbol = st.session_state.current_question
        bg_class = "question-even" if st.session_state.question_parity % 2 == 0 else "question-odd"
        st.markdown(f'<div class="{bg_class}"><div class="question">{a} {symbol} {b} = ?</div></div>', unsafe_allow_html=True)
        
        # 回答表示
        answer_display = st.session_state.current_answer if st.session_state.current_answer else "0"
        st.markdown(f'<div class="answer-display">{answer_display}</div>', unsafe_allow_html=True)
        
        # テンキー
        col1, col2, col3 = st.columns(3)
        
        # 数字ボタン（7-9）
        with col1:
            if st.button("7", key="btn_7", use_container_width=True):
                add_digit(7)
                st.rerun()
        with col2:
            if st.button("8", key="btn_8", use_container_width=True):
                add_digit(8)
                st.rerun()
        with col3:
            if st.button("9", key="btn_9", use_container_width=True):
                add_digit(9)
                st.rerun()
        
        # 数字ボタン（4-6）
        with col1:
            if st.button("4", key="btn_4", use_container_width=True):
                add_digit(4)
                st.rerun()
        with col2:
            if st.button("5", key="btn_5", use_container_width=True):
                add_digit(5)
                st.rerun()
        with col3:
            if st.button("6", key="btn_6", use_container_width=True):
                add_digit(6)
                st.rerun()
        
        # 数字ボタン（1-3）
        with col1:
            if st.button("1", key="btn_1", use_container_width=True):
                add_digit(1)
                st.rerun()
        with col2:
            if st.button("2", key="btn_2", use_container_width=True):
                add_digit(2)
                st.rerun()
        with col3:
            if st.button("3", key="btn_3", use_container_width=True):
                add_digit(3)
                st.rerun()
        
        # 最下段（0、クリア、バックスペース）
        with col1:
            if st.button("0", key="btn_0", use_container_width=True):
                add_digit(0)
                st.rerun()
        with col2:
            if st.button("⌫", key="btn_back", use_container_width=True):
                backspace()
                st.rerun()
        with col3:
            if st.button("C", key="btn_clear", use_container_width=True):
                clear_answer()
                st.rerun()
        
        # 回答ボタンと最初からやり直すボタン
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.button("🎯 回答する", key="submit_answer", use_container_width=True, type="primary")
        with col2:
            if st.button("🔄 やり直す", key="restart_game", use_container_width=True):
                reset_game()
                st.rerun()
        
        # 回答の値を取得
        try:
            answer_input = int(st.session_state.current_answer) if st.session_state.current_answer else 0
        except ValueError:
            answer_input = 0
            
        # 回答処理
        if submitted:
            answer_time = time.time() - st.session_state.question_start_time
            is_correct = answer_input == correct_answer
            
            # スコア計算（難易度に応じた係数を適用）
            points = calculate_score(answer_time, is_correct, st.session_state.difficulty)
            
            if is_correct:
                # 正解の場合
                st.session_state.score += points
                
                # 効果音を鳴らす
                play_sound("correct")
                
                # 時間に応じたメッセージ
                thresholds = SCORE_SETTINGS["time_thresholds"]
                if answer_time <= thresholds["fast"]:
                    message = f"スゴイ！ {thresholds['fast']}秒以内の回答で +{points}点！"
                elif answer_time <= thresholds["medium"]:
                    message = f"すばらしい！ {thresholds['medium']}秒以内の回答で +{points}点！"
                elif answer_time <= thresholds["slow"]:
                    message = f"よくできました！ {thresholds['slow']}秒以内の回答で +{points}点！"
                else:
                    message = f"正解です！ +{points}点"
                
                # 結果メッセージを保存（次の問題でも表示するため）
                st.session_state.last_result_message = {"text": message, "type": "correct"}
                
                # 結果を保存
                st.session_state.results.append({
                    "問題番号": st.session_state.question_count,
                    "問題": f"{a} {symbol} {b}",
                    "正解": correct_answer,
                    "回答": answer_input,
                    "正誤": "○",
                    "時間": answer_time,
                    "獲得点": points
                })
                
                # 次の問題に進む
                st.session_state.question_count += 1
                st.session_state.current_answer = ""  # 回答をクリア
                
                # ゲーム終了処理（main関数内の該当部分）
                if st.session_state.question_count >= GAME_SETTINGS["total_questions"]:
                    # ゲーム終了処理
                    end_time = time.time()
                    total_time = end_time - st.session_state.start_time
                    correct_count = len([r for r in st.session_state.results if r["正誤"] == "○"])
                    
                    print(f"ゲーム終了 - ユーザー: {st.session_state.current_user}, スコア: {st.session_state.score}, 正解数: {correct_count}/{len(st.session_state.results)}")
                    
                    # スコアを保存（全結果を渡す）
                    save_result = save_score(
                        st.session_state.current_user,
                        st.session_state.mode,
                        st.session_state.difficulty,
                        st.session_state.score,
                        correct_count,
                        int(total_time),
                        st.session_state.results
                    )
                    
                    if not save_result:
                        st.warning("スコアの保存に問題がありました。管理者に連絡してください。")
                    
                    st.session_state.game_complete = True
                else:
                    # パリティを切り替えて、背景色を交互に変える
                    st.session_state.question_parity += 1
                    st.session_state.current_question = generate_question(st.session_state.mode, st.session_state.difficulty)
                    st.session_state.question_start_time = time.time()
                
                st.rerun()
            else:
                # 不正解の場合
                st.session_state.score += points  # 負の値
                
                # 効果音を鳴らす
                play_sound("incorrect")
                
                message = f"残念！ 正しい答えは {correct_answer} です。 {points}点"
                # 結果メッセージを保存（次の問題でも表示するため）
                st.session_state.last_result_message = {"text": message, "type": "incorrect"}
                
                # 結果を保存
                st.session_state.results.append({
                    "問題番号": st.session_state.question_count,
                    "問題": f"{a} {symbol} {b}",
                    "正解": correct_answer,
                    "回答": answer_input,
                    "正誤": "×",
                    "時間": answer_time,
                    "獲得点": points
                })
                
                # 同じ問題を再度出題（質問開始時間をリセット）
                st.session_state.question_start_time = time.time()
                st.session_state.current_answer = ""  # 回答をクリア
                st.rerun()
    
    elif st.session_state.game_complete:
        # ゲーム終了、結果表示
        end_time = time.time()
        total_time = end_time - st.session_state.start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        st.markdown('<div class="subtitle">🎉 ゲーム終了！ 🎉</div>', unsafe_allow_html=True)
        
        # 結果カード
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align: center;">
            <h2 style="color: #673AB7;">結果発表</h2>
            <div style="font-size: 26px; margin: 10px 0;">プレイヤー: {USERS[st.session_state.current_user]['avatar']} {USERS[st.session_state.current_user]['name']}</div>
            <div style="font-size: 26px; margin: 10px 0;">モード: {st.session_state.mode}（{st.session_state.difficulty}）</div>
            <div style="font-size: 40px; color: #FF5733; font-weight: bold; margin: 20px 0;">スコア: {st.session_state.score}点</div>
            <div style="font-size: 24px; margin: 10px 0;">かかった時間: {minutes}分 {seconds}秒</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 結果の詳細分析
        st.markdown('<h3 style="text-align: center; color: #1976D2;">詳細分析</h3>', unsafe_allow_html=True)
        
        # 正解率の計算を修正（ゲーム終了画面内）
        df = pd.DataFrame(st.session_state.results)
        correct_count = len(df[df["正誤"] == "○"])
        incorrect_count = len(df[df["正誤"] == "×"])
        total_attempts = correct_count + incorrect_count  # 実際の試行回数

        col1, col2 = st.columns(2)
        with col1:
            # 正解率のドーナツグラフ（修正版）
            fig, ax = plt.subplots(figsize=(4, 4))
            if incorrect_count > 0:
                # 正解と不正解の回数でグラフ作成
                ax.pie([correct_count, incorrect_count], 
                    labels=["正解", "間違い"], 
                    colors=["#4CAF50", "#F44336"],
                    autopct='%1.1f%%',
                    startangle=90,
                    wedgeprops={'width': 0.5})
            else:
                # 全問正解の場合
                ax.pie([correct_count], 
                    labels=["正解"], 
                    colors=["#4CAF50"],
                    autopct='%1.1f%%',
                    startangle=90,
                    wedgeprops={'width': 0.5})
            ax.axis('equal')
            # 正解率のタイトルを修正
            ax.set_title(f"正解率 ({correct_count}/{total_attempts}回)")
            st.pyplot(fig)
        
        with col2:
            # 回答時間の分布
            if len(df) > 0:
                answer_times = df["時間"].tolist()
                fig, ax = plt.subplots(figsize=(4, 4))
                max_time = max(answer_times) if answer_times else 5
                thresholds = SCORE_SETTINGS["time_thresholds"]
                bins = [0, thresholds["fast"], thresholds["medium"], thresholds["slow"], max(max_time + 1, thresholds["slow"] + 1)]
                
                # ヒストグラムを作成してbinの数を確認
                n, bins_used, patches = ax.hist(answer_times, bins=bins)
                
                # binの数に合わせて色を調整
                colors = ["#4CAF50", "#8BC34A", "#FFEB3B", "#FF9800"]
                for i, patch in enumerate(patches):
                    if i < len(colors):
                        patch.set_facecolor(colors[i])
                    else:
                        patch.set_facecolor("#FF9800")  # デフォルト色
                
                ax.set_xlabel("回答時間 (秒)")
                ax.set_ylabel("回数")
                ax.set_title("回答時間分布")
                st.pyplot(fig)
            else:
                st.write("データがありません")
        
        # スコア内訳
        # 難易度に応じたスコア表示
        multiplier = DIFFICULTY_SETTINGS[st.session_state.difficulty]["score_multiplier"]
        thresholds = SCORE_SETTINGS["time_thresholds"]
        
        score_breakdown = {
            f"{SCORE_SETTINGS['time_bonus']['fast'] * multiplier}点（{thresholds['fast']}秒以内）": len(df[df["獲得点"] == SCORE_SETTINGS['time_bonus']['fast'] * multiplier]),
            f"{SCORE_SETTINGS['time_bonus']['medium'] * multiplier}点（{thresholds['medium']}秒以内）": len(df[df["獲得点"] == SCORE_SETTINGS['time_bonus']['medium'] * multiplier]),
            f"{SCORE_SETTINGS['time_bonus']['slow'] * multiplier}点（{thresholds['slow']}秒以内）": len(df[df["獲得点"] == SCORE_SETTINGS['time_bonus']['slow'] * multiplier]),
            f"{SCORE_SETTINGS['time_bonus']['very_slow'] * multiplier}点（{thresholds['slow']}秒超）": len(df[df["獲得点"] == SCORE_SETTINGS['time_bonus']['very_slow'] * multiplier]),
            f"{SCORE_SETTINGS['incorrect_penalty']}点（不正解）": len(df[df["獲得点"] == SCORE_SETTINGS["incorrect_penalty"]]),
        }
        
        st.markdown('<h4 style="text-align: center;">スコア内訳</h4>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        for i, (key, value) in enumerate(score_breakdown.items()):
            with [col1, col2, col3, col4, col5][i]:
                color = ["#4CAF50", "#8BC34A", "#CDDC39", "#FFEB3B", "#F44336"][i]
                st.markdown(f"""
                <div class="score-card" style="background-color: {color}20; border: 2px solid {color};">
                    <div style="font-size: 20px; font-weight: bold;">{key}</div>
                    <div style="font-size: 26px;">{value}回</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 問題の詳細を表示するオプション
        with st.expander("問題の詳細を表示"):
            if len(df) > 0:
                # 表示用にデータフレームを整形
                display_df = df.copy()
                display_df["時間"] = display_df["時間"].round(2).astype(str) + " 秒"
                st.dataframe(
                    display_df[["問題番号", "問題", "正解", "回答", "正誤", "時間", "獲得点"]],
                    use_container_width=True
                )
            else:
                st.write("データがありません")
        
        # 新しいゲームを始めるボタン
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("新しいゲームを始める", use_container_width=True, type="primary"):
            reset_game()
            st.rerun()

if __name__ == "__main__":
    main()