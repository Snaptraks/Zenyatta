import json
import numpy as np

import discord
from discord.ext import commands

from ..utils.gifs import random_gif


EMBED_COLOR = 0xF99E1A


class Overwatch(commands.Cog):
    """Commands for the GrandMasters."""

    def __init__(self, bot):
        self.bot = bot
        self.playing_overwatch = 0
        self.is_playing = False

    async def cog_load(self):

        with open("cogs/Overwatch/zenyatta.json", "r") as f:
            self.voice_lines = json.load(f)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Modify how many members are playing Overwatch, if it applies."""

        def is_game(x):
            return x.name == "Overwatch"

        if before.activities != after.activities and not before.bot:
            # print('Cog Overwatch.on_member_update was called, game changed!')

            try:
                if any(map(is_game, after.activities)):
                    self.playing_overwatch += 1

            except AttributeError:
                pass

            try:
                if any(map(is_game, before.activities)):
                    self.playing_overwatch -= 1

            except AttributeError:
                pass

            if self.playing_overwatch > 0 and not self.is_playing:
                await self.play_overwatch()

            elif self.playing_overwatch == 0 and self.is_playing:
                await self.stop_overwatch()

    @commands.Cog.listener()
    async def on_ready(self):
        """Initialize some parameters, such as the number or members
        currently in Overwatch.
        """
        all_members = set([m for m in self.bot.get_all_members() if not m.bot])

        def is_game(x):
            return x.name == "Overwatch"

        for m in all_members:
            try:
                if any(map(is_game, m.activities)):
                    self.playing_overwatch += 1
            except AttributeError:
                pass

        if self.playing_overwatch > 0:
            await self.play_overwatch()

    @commands.command(aliases=["decalre"])
    async def declare(self, ctx):
        """Send a gif to declare a game of Overwatch!"""

        # because xplio keeps making typos
        if ctx.invoked_with == "decalre":
            _ing = "decalring"
        else:
            _ing = "declaring"

        vl = (
            self.voice_lines["PreGame"]
            + self.voice_lines["Objective"]
            + self.voice_lines["Spawn"]
            + self.voice_lines["Ability"]
            + self.voice_lines["Fire"]
            + self.voice_lines["Healing"]
            + self.voice_lines["Kills"]
            + self.voice_lines["Ultimate"]
        )
        vl = np.random.choice(vl)
        gif_url = await random_gif(self.bot.http_session, "overwatch")
        description = f"{vl} {ctx.author.mention} is {_ing}, join the fight."

        embed = discord.Embed(description=description, color=EMBED_COLOR,).set_image(
            url=gif_url,
        )

        await ctx.send(embed=embed)

    @commands.Cog.listener(name="on_message")
    async def on_mention(self, message):
        """Send a Zenyatta voice line."""

        ctx = await self.bot.get_context(message)

        mentions = (
            self.voice_lines["Ability"]
            + self.voice_lines["Communication"]
            + self.voice_lines["Hello"]
        )

        if (
            ctx.me.mentioned_in(message)
            and not message.author.bot
            and not message.mention_everyone
            and not message.content.startswith(self.bot.command_prefix)
        ):

            out = np.random.choice(mentions)
            await message.channel.send(out)

    async def play_overwatch(self):
        self.is_playing = True
        await self.bot.change_presence(activity=discord.Game(name="Overwatch"))

    async def stop_overwatch(self):
        self.is_playing = False
        await self.bot.change_presence(activity=None)
