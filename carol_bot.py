#carol_bot.py
import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import asyncio
import random
import json
import google.generativeai as genai
from my_utils import load_prompt, load_memory, save_memory, is_active
import os
from keep_alive import keep_alive  # ← ファイル名と関数名はこれでOK

TOKEN = os.environ['CAROL_TOKEN']  # Secrets に設定したキー名

TOKEN = os.getenv("CAROL_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print(f"TOKEN: {TOKEN}")

keep_alive()

d2dad80 ('keep_alive.py')

# Gemini API設定
genai.configure(api_key=GEMINI_API_KEY)

# キャロルの設定
PROMPT_FILE = "inhabitant/prompts/carol.json"
MEMORY_FILE = "inhabitant/memory/carol.json"
EVENT_FILE = "inhabitant/events/carol_events.json"
ACTIVE_START = 8  # 朝8時から
ACTIVE_END = 24  # 夜12時まで

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

prompt = load_prompt(PROMPT_FILE)
memory = load_memory(MEMORY_FILE)


def load_memory(file_path):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}


# Geminiへのリクエスト関数
# Geminiへのリクエスト関数（プロンプトをちゃんと送る版）
async def get_gemini_response(user_message):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        full_prompt = f"{prompt}\n\nユーザー: {user_message}\nキャロル:"
        response = await asyncio.wait_for(asyncio.to_thread(
            model.generate_content, full_prompt),
                                          timeout=10)
        return response.text.strip()
    except asyncio.TimeoutError:
        print("Geminiの応答がタイムアウトしました")
        return "ごめん、ちょっと考えすぎちゃったみたい……"
    except Exception as e:
        print(f"Geminiエラー: {e}")
        return "ごめん、ちょっと今うまく返事できないみたい……"


# イベントを自動発生させる
@tasks.loop(minutes=30)
async def event_trigger():
    if not is_active(ACTIVE_START, ACTIVE_END):
        return
    channel = discord.utils.get(bot.get_all_channels(), name="living-room")
    if channel:
        with open(EVENT_FILE, "r", encoding="utf-8") as f:
            events_data = json.load(f)
        event_message = random.choice(events_data["events"])
        await channel.send(event_message)


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
    if message.author == bot.user:
        return

    await bot.process_commands(message)  # コマンドと通常メッセージを両方処理

    if not is_active(ACTIVE_START, ACTIVE_END):
        return

    if message.channel.name != "living-room":
        return

    user_message = message.content
    response_text = await get_gemini_response(user_message)

    # キャロルらしい自然な返しだけ送る
    await message.channel.send(response_text)

    # メモリに保存
    memory["last_message"] = message.content
    save_memory(MEMORY_FILE, memory)


if __name__ == "__main__":
    keep_alive()  # Webサーバー起動
    try:
        bot.run(TOKEN)  # Discordボット起動
    except Exception as e:
        print(f"Bot Error: {e}")
        os.system("kill")
