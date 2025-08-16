# 全てのst.experimental_rerun()をst.rerun()に置き換えたコード

import streamlit as st
import random
import time
import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt

# ページ設定
st.set_page_config(
    page_title="小学生の計算ゲーム",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSSスタイル
st.markdown("""
<style>
    .main-title {
        font-size: 42px;
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
        font-size: 40px;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin: 30px 0;
    }
    .correct {
        font-size: 24px;
        color: #4CAF50;
        text-align: center;
    }
    .incorrect {
        font-size: 24px;
        color: #F44336;
        text-align: center;
    }
    .score-display {
        font-size: 30px;
        font-weight: bold;
        color: #673AB7;
        text-align: center;
    }
    .time-display {
        font-size: 24px;
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
        margin: 20px 0;
    }
</style>
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

def generate_question(mode, difficulty):
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
            # 0～15の段の九九
            a = random.randint(0, 15)
            b = random.randint(0, 15)
            return a, b, a * b, "×"

def reset_game():
    st.session_state.game_started = False
    st.session_state.current_question = None
    st.session_state.question_count = 0
    st.session_state.score = 0
    st.session_state.start_time = None
    st.session_state.question_start_time = None
    st.session_state.game_complete = False
    st.session_state.results = []

def main():
    st.markdown('<div class="main-title">🧮 小学生の計算ゲーム 🧮</div>', unsafe_allow_html=True)
    
    if not st.session_state.game_started and not st.session_state.game_complete:
        # モードと難易度の選択
        st.markdown('<div class="subtitle">ゲームモードを選んでね！</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            mode = st.selectbox("計算の種類", ["足し算", "引き算", "掛け算"], index=0)
        with col2:
            difficulty = st.selectbox("むずかしさ", ["イージー", "ノーマル", "ハード"], index=0)
        
        # モード説明
        st.info(f"""
        **{mode}（{difficulty}）のルール**
        
        {'答えが一桁の足し算です。' if mode == "足し算" and difficulty == "イージー" else
         '一桁同士の足し算です。' if mode == "足し算" and difficulty == "ノーマル" else
         '二桁同士の足し算です。' if mode == "足し算" and difficulty == "ハード" else
         '一桁同士の引き算です。' if mode == "引き算" and difficulty == "イージー" else
         '二桁同士の引き算（繰り下がりなし）です。' if mode == "引き算" and difficulty == "ノーマル" else
         '二桁同士の引き算（繰り下がりあり）です。' if mode == "引き算" and difficulty == "ハード" else
         '0～5の段の九九です。' if mode == "掛け算" and difficulty == "イージー" else
         '0～9の段の九九です。' if mode == "掛け算" and difficulty == "ノーマル" else
         '0～15の段の九九です。'}
        
        **スコア計算：**
        - 1秒以内に正解：20点
        - 3秒以内に正解：15点
        - 5秒以内に正解：10点
        - それ以上の時間で正解：5点
        - 間違えた場合：-10点
        
        全部で50問あるよ！がんばって！
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
            st.session_state.current_question = generate_question(mode, difficulty)
            st.session_state.question_start_time = time.time()
            # ここを修正
            st.rerun()
    
    elif st.session_state.game_started and not st.session_state.game_complete:
        # 進捗バーの表示
        progress = st.session_state.question_count / 50
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.progress(progress)
        st.markdown(f'<div style="text-align: center;">問題 {st.session_state.question_count} / 50</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # スコア表示
        st.markdown(f'<div class="score-display">スコア: {st.session_state.score}</div>', unsafe_allow_html=True)
        
        # 経過時間表示
        elapsed_time = time.time() - st.session_state.start_time
        elapsed_str = str(timedelta(seconds=int(elapsed_time))).split(".")[0]
        st.markdown(f'<div class="time-display">時間: {elapsed_str}</div>', unsafe_allow_html=True)
        
        # 問題表示
        a, b, correct_answer, symbol = st.session_state.current_question
        st.markdown(f'<div class="question">{a} {symbol} {b} = ?</div>', unsafe_allow_html=True)
        
        # 回答欄
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            answer_input = st.number_input("答えを入力してください", min_value=0, step=1, key=f"answer_{st.session_state.question_count}")
            submitted = st.button("回答する", use_container_width=True)
            
        # 回答処理
        if submitted:
            answer_time = time.time() - st.session_state.question_start_time
            
            if answer_input == correct_answer:
                # 正解の場合
                if answer_time <= 1:
                    points = 20
                    message = "スゴイ！ 1秒以内の回答で +20点！"
                elif answer_time <= 3:
                    points = 15
                    message = "すばらしい！ 3秒以内の回答で +15点！"
                elif answer_time <= 5:
                    points = 10
                    message = "よくできました！ 5秒以内の回答で +10点！"
                else:
                    points = 5
                    message = "正解です！ +5点"
                
                st.session_state.score += points
                st.markdown(f'<div class="correct">{message}</div>', unsafe_allow_html=True)
                
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
                
                if st.session_state.question_count >= 50:
                    st.session_state.game_complete = True
                else:
                    st.session_state.current_question = generate_question(st.session_state.mode, st.session_state.difficulty)
                    st.session_state.question_start_time = time.time()
                
                # ここを修正
                st.rerun()
            else:
                # 不正解の場合
                st.session_state.score -= 10
                st.markdown(f'<div class="incorrect">残念！ 正しい答えは {correct_answer} です。 -10点</div>', unsafe_allow_html=True)
                
                # 結果を保存
                st.session_state.results.append({
                    "問題番号": st.session_state.question_count,
                    "問題": f"{a} {symbol} {b}",
                    "正解": correct_answer,
                    "回答": answer_input,
                    "正誤": "×",
                    "時間": answer_time,
                    "獲得点": -10
                })
                
                # 同じ問題を再度出題（質問開始時間をリセット）
                st.session_state.question_start_time = time.time()
                # ここを修正
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
            <div style="font-size: 26px; margin: 10px 0;">モード: {st.session_state.mode}（{st.session_state.difficulty}）</div>
            <div style="font-size: 40px; color: #FF5733; font-weight: bold; margin: 20px 0;">スコア: {st.session_state.score}点</div>
            <div style="font-size: 24px; margin: 10px 0;">かかった時間: {minutes}分 {seconds}秒</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 結果の詳細分析
        st.markdown('<h3 style="text-align: center; color: #1976D2;">詳細分析</h3>', unsafe_allow_html=True)
        
        # 正解率の計算
        df = pd.DataFrame(st.session_state.results)
        correct_count = len(df[df["正誤"] == "○"])
        incorrect_count = len(df[df["正誤"] == "×"])
        total_attempts = correct_count + incorrect_count
        accuracy_rate = correct_count / 50 * 100
        
        col1, col2 = st.columns(2)
        with col1:
            # 正解率のドーナツグラフ
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie([correct_count, incorrect_count - 50], 
                  labels=["正解", "間違い"], 
                  colors=["#4CAF50", "#F44336"],
                  autopct='%1.1f%%',
                  startangle=90,
                  wedgeprops={'width': 0.5})
            ax.axis('equal')
            plt.title("問題の正解率")
            st.pyplot(fig)
        
        with col2:
            # 回答時間の分布
            answer_times = df["時間"].tolist()
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.hist(answer_times, bins=[0, 1, 3, 5, max(answer_times)], 
                   color=["#4CAF50", "#8BC34A", "#FFEB3B", "#FF9800"])
            ax.set_xlabel("回答時間（秒）")
            ax.set_ylabel("回数")
            plt.title("回答時間の分布")
            st.pyplot(fig)
        
        # スコア内訳
        score_breakdown = {
            "20点（1秒以内）": len(df[df["獲得点"] == 20]),
            "15点（3秒以内）": len(df[df["獲得点"] == 15]),
            "10点（5秒以内）": len(df[df["獲得点"] == 10]),
            "5点（5秒超）": len(df[df["獲得点"] == 5]),
            "-10点（不正解）": len(df[df["獲得点"] == -10]),
        }
        
        st.markdown('<h4 style="text-align: center;">スコア内訳</h4>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        for i, (key, value) in enumerate(score_breakdown.items()):
            with [col1, col2, col3, col4, col5][i]:
                color = ["#4CAF50", "#8BC34A", "#CDDC39", "#FFEB3B", "#F44336"][i]
                st.markdown(f"""
                <div class="score-card" style="background-color: {color}20; border: 2px solid {color};">
                    <div style="font-size: 22px; font-weight: bold;">{key}</div>
                    <div style="font-size: 28px;">{value}回</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 新しいゲームを始めるボタン
        if st.button("新しいゲームを始める", use_container_width=True):
            reset_game()
            # ここを修正
            st.rerun()

if __name__ == "__main__":
    main()