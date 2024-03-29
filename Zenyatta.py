import logging

import discord
from discord.ext import commands
from snapcogs import Bot

import config


def main():
    intents = discord.Intents.all()
    allowed_mentions = discord.AllowedMentions(replied_user=False)

    startup_extensions = [
        "cogs.Overwatch",
        "cogs.SeaofThieves",
        "cogs.General",
        "snapcogs.Admin",
        "snapcogs.Fun",
        "snapcogs.Poll",
        "snapcogs.Roles",
        "snapcogs.Information",
        "snapcogs.Tips",
        "snapcogs.Link",
    ]

    bot = Bot(
        description="One cannot survive on strength alone.",
        command_prefix=commands.when_mentioned_or("!"),
        help_command=commands.DefaultHelpCommand(dm_help=False),
        intents=intents,
        allowed_mentions=allowed_mentions,
        db_name="db/Zenyatta.db",
        startup_extensions=startup_extensions,
    )

    bot.run(config.token, log_level=logging.WARNING)


if __name__ == "__main__":
    main()
