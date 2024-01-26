import logging
from datetime import datetime, time, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import format_dt
from snapcogs import Bot

from ..utils.gifs import random_gif
from . import views

LOGGER = logging.getLogger(__name__)

PIRATE_ROLE = 787415779745595392
# SEA_OF_THIEVES_CHANNEL = 759799574289186896
SEA_OF_THIEVES_CHANNEL = 588171779957063680
GOLD_RUSH_DURATION_HOURS = 1
GOLD_RUSH_STARTS = [
    time(hour=1, tzinfo=timezone.utc),
    time(hour=17, tzinfo=timezone.utc),
]
GOLD_RUSH_ENDS = [
    gr_start.replace(hour=gr_start.hour + GOLD_RUSH_DURATION_HOURS)
    for gr_start in GOLD_RUSH_STARTS
]
GOLD_RUSH_PERIODS = [
    [gr_start, gr_end] for gr_start, gr_end in zip(GOLD_RUSH_STARTS, GOLD_RUSH_ENDS)
]
GR_COIN = "\N{COIN}"
GOLD_RUSH_PREFIX = f"{GR_COIN} Gold Rush is now! {GR_COIN} "


def datetime_replace_time(dt: datetime, t: time) -> datetime:
    """Replace the hour, minute, second, and microsecond part of a datetime
    with those in the time object.
    """

    return dt.replace(
        hour=t.hour,
        minute=t.minute,
        second=t.second,
        microsecond=t.microsecond,
    )


class SeaofThieves(commands.Cog):
    """Commands for Sea of Thieves related activities."""

    def __init__(self, bot: Bot):
        self.bot = bot
        LOGGER.debug("Starting Gold Rush")
        self.gold_rush_start.start()
        self.gold_rush_end.start()

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

    @app_commands.command(name="gold-rush")
    async def gold_rush_command(self, interaction: discord.Interaction):
        """Check when is the next Gold Rush event, or if we are currently in one."""

        dt_now = discord.utils.utcnow()
        time_now = dt_now.time().replace(tzinfo=timezone.utc)
        # time_now = time(1, 30, tzinfo=timezone.utc)

        for gr_start, gr_end in GOLD_RUSH_PERIODS:
            if gr_start <= time_now < gr_end:
                dt_end = datetime_replace_time(dt_now, gr_end)
                await interaction.response.send_message(
                    f"{GR_COIN} We are in Gold Rush until {format_dt(dt_end, 't')} "
                    f"({format_dt(dt_end, 'R')}).",
                    ephemeral=True,
                )
                # No need to continue if we are in a gold rush event
                return

        # check for next gold rush event
        next_starts = [
            datetime_replace_time(dt_now, GOLD_RUSH_STARTS[0]),
            datetime_replace_time(dt_now, GOLD_RUSH_STARTS[1]),
            # check for first gold rush tomorrow too
            datetime_replace_time(dt_now + timedelta(days=1), GOLD_RUSH_STARTS[0]),
        ]
        for gr_start in next_starts:
            if dt_now <= gr_start:
                await interaction.response.send_message(
                    f"{GR_COIN} Next Gold Rush at {format_dt(gr_start, 't')} "
                    f"({format_dt(gr_start, 'R')}).",
                    ephemeral=True,
                )
                # stop checking for events!
                break

    @tasks.loop(time=GOLD_RUSH_STARTS)
    async def gold_rush_start(self):
        """Change the channel topic to indicate when Gold Rush events are happening."""

        channel = self.bot.get_channel(SEA_OF_THIEVES_CHANNEL)

        if isinstance(channel, discord.TextChannel):
            new_topic = f"{GOLD_RUSH_PREFIX}{channel.topic or ''}"
            channel = await channel.edit(topic=new_topic)
            LOGGER.debug(f"{new_topic=}")

    @tasks.loop(time=GOLD_RUSH_ENDS)
    async def gold_rush_end(self):
        """Revert the channel topic without the Gold Rush information."""

        channel = self.bot.get_channel(SEA_OF_THIEVES_CHANNEL)

        if isinstance(channel, discord.TextChannel):
            if channel.topic is None:
                return

            clean_topic = channel.topic.removeprefix(GOLD_RUSH_PREFIX)
            await channel.edit(topic=clean_topic)
            LOGGER.debug(f"{clean_topic=}")

    @gold_rush_start.before_loop
    async def gold_rush_before(self):
        """Wait for the bot to be ready."""

        LOGGER.debug("Waiting for bot to be ready before Gold Rush")
        await self.bot.wait_until_ready()
