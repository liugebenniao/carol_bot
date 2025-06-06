import json
import os
from datetime import datetime
import config # 設定ファイルをインポート

def load_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)["prompt"]

def load_memory(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- 親密度関連の関数 ---
def load_affinity(user_id):
    if not os.path.exists(config.AFFINITY_FILE):
        return 0
    with open(config.AFFINITY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(str(user_id), 0)

def save_affinity(user_id, value):
    if os.path.exists(config.AFFINITY_FILE):
        with open(config.AFFINITY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    data[str(user_id)] = value
    with open(config.AFFINITY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- 時間チェック関数 ---
def is_active():
    now_hour = datetime.now(config.JST).hour
    start, end = config.ACTIVE_START, config.ACTIVE_END
    if end < start:  # 日をまたぐ場合
        return now_hour >= start or now_hour < end
    return start <= now_hour < end
