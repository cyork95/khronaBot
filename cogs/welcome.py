import discord
from discord.ext import commands
from discord import app_commands
import settings

logger = settings.LOGGER


class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Greeting Command
    @app_commands.command(name="greetings", description="Greets the user")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Greetings human!")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.__class__.__name__} cog has been loaded.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
    await bot.tree.sync()
