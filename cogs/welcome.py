import discord

import settings
import random
from discord.ext import commands

logger = settings.LOGGER


class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot



async def setup(bot):
    await bot.add_cog(Welcome(bot))
