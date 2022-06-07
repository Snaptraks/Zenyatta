import asyncio

import discord
from discord.ext import commands
from snapcogs import Bot

import config


async def main():
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
    ]

    bot = Bot(
        description="One cannot survive on strength alone.",
        command_prefix="!",
        help_command=commands.DefaultHelpCommand(dm_help=False),
        intents=intents,
        allowed_mentions=allowed_mentions,
        db_name="db/Zenyatta.db",
        startup_extensions=startup_extensions,
    )

    async with bot:
        await bot.start(config.token)


if __name__ == "__main__":
    asyncio.run(main())
