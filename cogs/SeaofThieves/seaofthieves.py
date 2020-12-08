import itertools
import json
import os
import random

import discord
from discord.ext import commands
from ..utils.gifs import random_gif


COG_PATH = os.path.dirname(__file__)
EMBED_COLOR = 0x2C8C77


class SeaofThieves(commands.Cog):
    """Commands for Sea of Thieves related activities."""

    def __init__(self, bot):
        self.bot = bot

        with open(os.path.join(COG_PATH, "chat_wheel.json")) as f:
            self.chat_wheel = json.load(f)

    @commands.command(aliases=["yar"])
    async def yarr(self, ctx):
        """Gather mateys to sail the Sea of Thieves!"""

        all_chat = itertools.chain.from_iterable(self.chat_wheel.values())
        valid_ends = (".", "!", "?", "*")
        valid_chats = set([x for x in all_chat if x.endswith(valid_ends)])
        if ctx.author.id == 242465567259230208:  # Elerinna
            random_chat = f":rainbow: {self.chat_wheel['alerts'][-1]}"
        else:
            random_chat = random.choice(list(valid_chats))

        description = (
            f"**{random_chat}**\n{ctx.author.mention} sails today, "
            "join in on the plunder!"
        )
        gif_url = await random_gif(self.bot.http_session, "pirate")

        embed = discord.Embed(
            description=description,
            color=EMBED_COLOR,
        ).set_image(
            url=gif_url,
        )

        await ctx.send(embed=embed)
