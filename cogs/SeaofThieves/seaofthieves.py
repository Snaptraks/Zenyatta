from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands

# from . import menus
from . import views
from ..utils.gifs import random_gif


class SeaofThieves(commands.Cog):
    """Commands for Sea of Thieves related activities."""

    def __init__(self, bot):
        self.bot = bot
        self.pirate_role = defaultdict(lambda: None)
        self.skull_emoji = defaultdict(lambda: None)

    @commands.hybrid_command(aliases=["yar"])
    @app_commands.guilds()
    async def yarr(self, ctx):
        """Gather mateys to sail the Sea of Thieves!"""

        guild_id = ctx.guild.id
        if self.pirate_role[guild_id] is None:
            role = discord.utils.get(ctx.guild.roles, name="Pirate")
            if role is None:
                role = ctx.guild.default_role
            self.pirate_role[guild_id] = role

        if self.skull_emoji[guild_id] is None:
            self.skull_emoji[guild_id] = discord.PartialEmoji.from_str(
                "<:sea_of_thieves:788880548369006603>"
            )

        gif_url = await random_gif(self.bot.http_session, "sea of thieves")
        view = views.YarrView(ctx.author, self.skull_emoji[guild_id])
        embed = view.build_embed(gif_url)

        await ctx.send(self.pirate_role[guild_id].mention, embed=embed, view=view)
