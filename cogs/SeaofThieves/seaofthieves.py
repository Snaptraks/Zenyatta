import asyncio
import logging
from datetime import time, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks
from snapcogs import Bot

from ..utils.gifs import random_gif
from . import views

LOGGER = logging.getLogger(__name__)

PIRATE_ROLE = 787415779745595392
SEA_OF_THIEVES_CHANNEL = 759799574289186896
GOLD_RUSH_TIMES = [
    time(hour=17, tzinfo=timezone.utc),
    time(hour=1, tzinfo=timezone.utc),
]
GOLD_RUSH_DURATION = 3600  # seconds == 1 hour


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

    @tasks.loop(time=GOLD_RUSH_TIMES)
    async def gold_rush(self):
        """Change the channel topic to indicate when Gold Rush events are happening."""

        channel = self.bot.get_channel(SEA_OF_THIEVES_CHANNEL)
        topic_prefix = "\N{COIN} Gold Rush is now! \N{COIN} "

        if isinstance(channel, discord.TextChannel):
            new_topic = f"{topic_prefix}{channel.topic}"
            channel = await channel.edit(topic=new_topic)
            LOGGER.debug(f"{new_topic=}")
            await asyncio.sleep(GOLD_RUSH_DURATION)
            if channel.topic is None:
                return

            clean_topic = channel.topic.removeprefix(topic_prefix)
            await channel.edit(topic=clean_topic)
            LOGGER.debug(f"{clean_topic=}")

    @gold_rush.before_loop
    async def gold_rush_before(self):
        """Wait for the bot to be ready."""

        LOGGER.debug("Waiting for bot to be ready before Gold Rush")
        await self.bot.wait_until_ready()
