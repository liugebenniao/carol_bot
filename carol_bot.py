import discord
from discord.ext import commands
import os
import asyncio
import time
import config
import my_utils
from keep_alive import keep_alive

# Botの基本設定
intents = discord.Intents.default()
intents.message_content = True

class CarolBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        # ボット全体で共有したい状態をここに定義
        self.last_message_time = None
        
        # 起動時に会話モードをファイルから読み込む
        memory = my_utils.load_memory(config.MEMORY_FILE)
        self.conversation_enabled = memory.get("conversation_enabled", True)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print(f"Conversation mode is {'ON' if self.conversation_enabled else 'OFF'}")

    async def setup_hook(self):
        # cogsフォルダから.pyファイルを検索してロードする
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded Cog: {filename}")
        
        # スラッシュコマンドを同期
        try:
            synced = await self.tree.sync(guild=discord.Object(id=config.GUILD_ID))
            print(f"Synced {len(synced)} command(s)!")
        except Exception as e:
            print(f"Command sync failed: {e}")

async def main():
    bot = CarolBot()
    keep_alive() # Webサーバーを起動して常時起動
    try:
        await bot.start(config.TOKEN)
    except Exception as e:
        print(f"Bot Error: {e}")
        os.system("kill 1")

if __name__ == "__main__":
    asyncio.run(main())
