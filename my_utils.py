# utils.py
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def load_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_memory(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def save_memory(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
