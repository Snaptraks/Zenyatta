from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands

from . import views
from ..utils.gifs import random_gif


class SeaofThieves(commands.Cog):
    """Commands for Sea of Thieves related activities."""

    def __init__(self, bot: Bot):
        self.bot = bot
        LOGGER.debug("Starting Gold Rush")
        self.gold_rush.start()

    @commands.hybrid_command(aliases=["yar"])
    @app_commands.describe(message="What's the plan, captain?")
    async def yarr(self, ctx, *, message: str = ""):
        """Gather mateys to sail the Sea of Thieves!"""

        role = ctx.guild.get_role(PIRATE_ROLE)
        if role is None:
            role = ctx.guild.default_role

        gif_url = await random_gif(self.bot.http_session, "sea of thieves")
        view = views.YarrView(ctx.author)
        embed = view.build_embed(gif_url)

        await ctx.send(f"{role.mention}\n{message}", embed=embed, view=view)
