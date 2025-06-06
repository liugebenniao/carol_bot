import os
from datetime import timezone, timedelta

# --- 基本設定 ---
TOKEN = os.environ["CAROL_TOKEN"]
GUILD_ID = os.environ["GUILD_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# --- ボットの挙動設定 ---
ACTIVE_START = 8  # 活動開始時間（午前8時）
ACTIVE_END = 1    # 活動終了時間（午前1時）
LIVING_ROOM_CHANNEL = "living-room" # 反応するチャンネル名

# --- ファイルパス ---
PROMPT_FILE = "prompts/carol.json"
MEMORY_FILE = "memory/carol.json"
EVENT_FILE = "events/carol_events.json"
AFFINITY_FILE = "memory/affinity.json"

# --- その他 ---
JST = timezone(timedelta(hours=9))
GOODBYE_KEYWORDS = ["おやすみ", "またね", "ばいばい", "さようなら"]

# --- Gemini API 設定 ---
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
