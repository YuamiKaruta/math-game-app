# config.py
import os
from pathlib import Path

# データ保存パス設定（明示的に絶対パスを指定）
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))  # スクリプトのあるディレクトリ
SOUND_DIR = BASE_DIR / "sound"
SOUND_FILES = {
    "correct": "correct.mp3",
    "incorrect": "incorrect.mp3"
}
DATA_DIR = BASE_DIR / "data"
SCORES_FILE = DATA_DIR / "scores.json"

# ゲームの基本設定
GAME_SETTINGS = {
    "total_questions": 10,  # 1ゲームあたりの問題数
    "max_answer_digits": 4,  # 回答の最大桁数
}

# ユーザー設定
USERS = {
    "user1": {"name": "あずさ", "avatar": "👧🏻"},
    "user2": {"name": "ももか", "avatar": "👧🏼"},
    # 必要に応じて追加
}

# デフォルトユーザー
DEFAULT_USER = "user1"

# 難易度設定
DIFFICULTY_SETTINGS = {
    "イージー": {
        "score_multiplier": 1,  # スコア係数
        "足し算": "答えが一桁の足し算です。",
        "引き算": "一桁同士の引き算です。",
        "掛け算": "0～5の段の九九です。",
    },
    "ノーマル": {
        "score_multiplier": 2,  # スコア係数
        "足し算": "一桁同士の足し算です。",
        "引き算": "二桁同士の引き算（繰り下がりなし）です。",
        "掛け算": "0～9の段の九九です。",
    },
    "ハード": {
        "score_multiplier": 3,  # スコア係数
        "足し算": "二桁同士の足し算です。",
        "引き算": "二桁同士の引き算（繰り下がりあり）です。",
        "掛け算": "0～15の段の九九です。",
    }
}

# スコア設定
SCORE_SETTINGS = {
    "time_thresholds": {
        "fast": 3,     # 高速回答の閾値（秒）
        "medium": 5,   # 中速回答の閾値（秒）
        "slow": 10      # 低速回答の閾値（秒）
    },
    "time_bonus": {
        "fast": 20,    # 高速回答のボーナス
        "medium": 15,  # 中速回答のボーナス
        "slow": 10,    # 低速回答のボーナス
        "very_slow": 5 # 非常に遅い回答のボーナス
    },
    "incorrect_penalty": -10  # 不正解のペナルティ
}

# 効果音設定（Base64エンコードされたごく短い音声データ）
SOUND_EFFECTS = {
    "correct": "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLHPH7tiJNwgZVrPn4aRNGRFCltDq0mc0KDpqrN/lu2kpLxlQnN/z33VDQSJR4+9OIQw5rNyxOA1l3tKiVXGy2fWdRDyywPehQumm0eC7Z7Ka6d+8eCK+sf7qtbf9Ac++SQHEpOj7yc5GFMCgGPG/wrzt1UTLpT70s8fAb0W7sjTls83dy7qtoH8wp+yhuQALtZf0xrBE+bqhntX/4+bbyd+hkLPWztDr6NapjNfGt9W8n+zmtLjisKqV3MKwluPas6/C4bOj6cSsi+C0tZbE+OJ3SjoAAAAAAAAAAAA=",
    "incorrect": "data:audio/wav;base64,UklGRpYDAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YXIDAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLHPH7tiJNwgZVrPn4aRNGRFCltDq0mc0KDpqrN/lu2kpLxlQnNLL0j8sNFB72Ml7KhgC68DX9t3O6+Xm7/vw3LS4xtDLu7O/2ufox66+1dje0ru5yOPx5Mq2veHe18vCt77k7uPOuLnh6OPVvcG6volIAAAAAAAAAAAA"
}

# スコア保存形式を拡張（間違えた問題の履歴を追加）
HISTORY_MAX_MISTAKES = 50  # ユーザーごとに保存する間違えた問題の最大数

# データ保存ディレクトリがなければ作成（起動時に必ず実行）
os.makedirs(DATA_DIR, exist_ok=True)
print(f"データディレクトリを確認/作成: {DATA_DIR}")

# データディレクトリ作成
os.makedirs(SOUND_DIR, exist_ok=True)