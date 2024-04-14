import discord
from discord.ext import commands
from discord import app_commands
import settings
import random

logger = settings.LOGGER


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._synced = False  # Prevents multiple syncs in case of reconnections

    async def cog_load(self):
        # Placeholder for any specific cog initialization if needed
        pass



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
    await bot.add_cog(Utility(bot))
    # Since syncing in `on_ready` could be delayed, you might consider initial sync here if necessary
