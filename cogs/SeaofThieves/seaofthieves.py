from collections import defaultdict

import discord
from discord.ext import commands
from . import menus


class SeaofThieves(commands.Cog):
    """Commands for Sea of Thieves related activities."""

    def __init__(self, bot):
        self.bot = bot
        self.pirate_role = defaultdict(lambda: None)

    @commands.command(aliases=["yar"])
    async def yarr(self, ctx):
        """Gather mateys to sail the Sea of Thieves!"""

        if self.pirate_role[ctx.guild.id] is None:
            role = discord.utils.get(
                ctx.guild.roles, name="Pirate")
            if role is None:
                role = ctx.guild.default_role
            self.pirate_role[ctx.guild.id] = role

        menu = menus.YarrMenu(
            timeout=None,
            pirate_role=self.pirate_role[ctx.guild.id],
        )
        await menu.start(ctx)
