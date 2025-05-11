#carol_bot.py
import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import asyncio
import random
import json
import google.generativeai as genai
from my_utils import load_prompt, load_memory, save_memory
from keep_alive import keep_alive
keep_alive()
import time
from datetime import datetime, timedelta, timezone

TOKEN = os.environ["CAROL_TOKEN"]
GUILD_ID = os.environ["GUILD_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
ACTIVE_START = 8   # 午前8時
ACTIVE_END = 1    # 午前1時

# グローバル変数の初期化
last_message_time = 0

# Gemini API設定
genai.configure(api_key=GEMINI_API_KEY)

# キャロルの設定
PROMPT_FILE = "prompts/carol.json"
MEMORY_FILE = "memory/carol.json"
EVENT_FILE = "events/carol_events.json"

def is_active(start, end):
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst).hour
    if end < start:  # 例: 22〜2時など日をまたぐ場合
        return now >= start or now < end
    return start <= now < end


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

prompt = load_prompt(PROMPT_FILE)
memory = load_memory(MEMORY_FILE)

# Geminiへのリクエスト関数
async def get_gemini_response(user_message):
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash",
        safety_settings=[
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE"
        },
    ]
)
        full_prompt = f"{prompt}\n\nユーザー: {user_message}\nキャロル:"
        response = await asyncio.wait_for(
    asyncio.to_thread(model.generate_content, full_prompt),
    timeout=10
)
        return response.text.strip()
    except asyncio.TimeoutError:
        print("Geminiの応答がタイムアウトしました")
        return "ごめん、ちょっと考えすぎちゃったみたい……"
    except Exception as e:
        error_message = f"ごめん、ちょっと今うまく返事できないみたい……（エラー: {e}）"
        print(f"Geminiエラー: {e}", flush=True)
        return error_message


# イベントを自動発生させる
@tasks.loop(minutes=30)
async def event_trigger():
    global last_message_time
    if not is_active(ACTIVE_START, ACTIVE_END):
        return

    current_time = time.time()
    if current_time - last_message_time >= 600:
        channel = discord.utils.get(bot.get_all_channels(), name="living-room")
        if channel:
            try:
                with open(EVENT_FILE, "r", encoding="utf-8") as f:
                    events_data = json.load(f)
                event_message = random.choice(events_data["events"])
                await channel.send(event_message)
            except Exception as e:
                print(f"イベント送信エラー: {e}")


# 起動時に実行
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Synced {len(synced)} command(s)!")
    except Exception as e:
        print(e)
    event_trigger.start()


# スラッシュコマンド: ダイスを振る
@bot.tree.command(name="dice",
                  description="サイコロを振る",
                  guild=discord.Object(id=GUILD_ID))
async def dice(interaction: discord.Interaction, message: str):
    result = random.choice(["成功！", "失敗……"])
    await interaction.response.send_message(f"{message}\n判定結果: {result}")


# メッセージに反応
@bot.event
async def on_message(message):
    global last_message_time

    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if not is_active(ACTIVE_START, ACTIVE_END):
        return

    if message.channel.name != "living-room":
        return

    user_message = message.content
    response_text = await get_gemini_response(user_message)
    await asyncio.sleep(random.uniform(1.0, 3.0))
    await message.channel.send(response_text)

    memory["last_message"] = message.content
    save_memory(MEMORY_FILE, memory)

    if message.content:
        last_message_time = time.time()


if __name__ == "__main__":
    try:
        bot.run(TOKEN)  # Discordボット起動
    except Exception as e:
        print(f"Bot Error: {e}")
        os.system("kill")
