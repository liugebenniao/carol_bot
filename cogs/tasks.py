import discord
from discord.ext import commands, tasks
import random
import json
import config
import my_utils

class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_trigger.start()

    def cog_unload(self):
        self.event_trigger.cancel()

    @tasks.loop(minutes=30)
    async def event_trigger(self):
        # ボットが準備完了するまで待つ
        await self.bot.wait_until_ready()

        if not my_utils.is_active():
            return
            
        # 10分以上会話がなければイベントを発生
        if self.bot.last_message_time and (discord.utils.utcnow() - self.bot.last_message_time).total_seconds() >= 600:
            channel = discord.utils.get(self.bot.get_all_channels(), name=config.LIVING_ROOM_CHANNEL)
            if channel:
                try:
                    with open(config.EVENT_FILE, "r", encoding="utf-8") as f:
                        events_data = json.load(f)
                    event_message = random.choice(events_data["events"])
                    await channel.send(event_message)
                    # イベントを投稿したら、次のイベントまで時間をリセットする
                    self.bot.last_message_time = discord.utils.utcnow()
                except Exception as e:
                    print(f"イベント送信エラー: {e}")

async def setup(bot):
    await bot.add_cog(TasksCog(bot))
