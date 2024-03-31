import discord
from discord.ext import commands
from discord import app_commands
import settings
import random

logger = settings.LOGGER


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._synced = False  # Prevents multiple syncs in case of reconnections

    async def cog_load(self):
        # Placeholder for any specific cog initialization if needed
        pass

    @app_commands.command(name='log', description='Responds with a simple message about logging.')
    async def log(self, interaction: discord.Interaction):
        response = "Hello! I'm alive and logging."
        await interaction.response.send_message(response)
        logger.info(f"Responded to test command in {interaction.guild.name}.")

    @app_commands.command(name='say', description='Repeats what you say.')
    @app_commands.describe(message='The message to repeat.')
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)
        logger.info(f"Responded to say command in {interaction.guild.name} with \"{message}\".")

    @app_commands.command(name='choose', description='Chooses from the given options.')
    @app_commands.describe(options='The options to choose from, separated by commas.')
    async def choose(self, interaction: discord.Interaction, options: str):
        choices = [option.strip() for option in options.split(',')]
        choice = random.choice(choices)
        await interaction.response.send_message(choice)
        logger.info(f"Made a choice in {interaction.guild.name}: \"{choice}\".")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self._synced:
            # Optionally, limit to specific guilds during development
            # for guild_id in [123456789012345678, 987654321098765432]:
            #     await self.bot.tree.sync(guild=discord.Object(id=guild_id))

            # For production, sync commands globally (this can take up to 1 hour to propagate)
            await self.bot.tree.sync()

            # To immediately sync commands to all guilds the bot is part of:
            # for guild in self.bot.guilds:
            #     await self.bot.tree.sync(guild=guild)

            print("Commands synced.")
            self._synced = True


async def setup(bot):
    await bot.add_cog(Basic(bot))
    # Since syncing in `on_ready` could be delayed, you might consider initial sync here if necessary
