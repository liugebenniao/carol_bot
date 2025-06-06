import discord
from discord import app_commands
from discord.ext import commands
import random
import config
import my_utils

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dice", description="サイコロを振る")
    async def dice(self, interaction: discord.Interaction, message: str):
        result = random.choice(["成功！", "失敗……"])
        await interaction.response.send_message(f"{message}\n判定結果: {result}")

    @app_commands.command(name="toggle_conversation", description="キャロルの会話モードをオン/オフにします")
    async def toggle_conversation(self, interaction: discord.Interaction):
        self.bot.conversation_enabled = not self.bot.conversation_enabled
        # 状態をファイルに保存
        memory = my_utils.load_memory(config.MEMORY_FILE)
        memory["conversation_enabled"] = self.bot.conversation_enabled
        my_utils.save_memory(config.MEMORY_FILE, memory)
        status = "オン" if self.bot.conversation_enabled else "オフ"
        await interaction.response.send_message(f"会話モードを{status}にしました")

    @app_commands.command(name="affinity", description="キャロルとの親密度を確認します")
    async def check_affinity(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        affinity = my_utils.load_affinity(user_id)
        
        if affinity >= 100: comment = "…だいすき！"
        elif affinity >= 50: comment = "ともだち！"
        elif affinity >= 10: comment = "いいかんじかも"
        else: comment = "まだまだこれから"
            
        await interaction.response.send_message(f"{interaction.user.display_name} との親密度: {affinity}/100\n{comment}")

async def setup(bot):
    await bot.add_cog(CommandsCog(bot), guild=discord.Object(id=config.GUILD_ID))
