import discord
from discord.ext import commands
import google.generativeai as genai
import asyncio
import config
import my_utils

class ConversationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prompt = my_utils.load_prompt(config.PROMPT_FILE)
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            safety_settings=config.SAFETY_SETTINGS
        )

    def build_prompt(self, user_id):
        affinity = my_utils.load_affinity(user_id)
        affinity_comment = ""
        if affinity >= 100:
            affinity_comment = "Extremely intimate, almost like lovers"
        elif affinity >= 50:
            affinity_comment = "Very close friends"
        elif affinity >= 10:
            affinity_comment = "Friends"
        else:
            affinity_comment = "Getting to know each other"
        return f"{self.prompt}\n\n現在の親密度: {affinity}\n{affinity_comment}"

    async def get_gemini_response(self, user_message, user_id):
        try:
            full_prompt = f"{self.build_prompt(user_id)}\n\nユーザー: {user_message}\nキャロル:"
            response = await asyncio.to_thread(self.model.generate_content, full_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Geminiエラー: {e}", flush=True)
            return "ごめん、ちょっと今うまく返事できないみたい……"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return
        
        if not my_utils.is_active() or message.channel.name != config.LIVING_ROOM_CHANNEL or not self.bot.conversation_enabled:
            return

        user_message = message.content
        if not user_message:
            return

        async with message.channel.typing():
            response_text = await self.get_gemini_response(user_message, message.author.id)
            await asyncio.sleep(1) # 少し待ってから送信
            await message.channel.send(response_text)

        # 親密度を更新
        current_affinity = my_utils.load_affinity(message.author.id)
        bonus = 2 if "ありがとう" in user_message else 0
        new_affinity = min(current_affinity + 1 + bonus, 100)
        my_utils.save_affinity(message.author.id, new_affinity)

        # 最後のメッセージ時刻を更新
        self.bot.last_message_time = discord.utils.utcnow()

async def setup(bot):
    await bot.add_cog(ConversationCog(bot))