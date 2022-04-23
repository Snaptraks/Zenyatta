import asyncio
from datetime import datetime

import aiosqlite
import aiohttp
import discord
from discord.ext import commands

import config


class Zenyatta(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.db_name = kwargs.get("db_name", ":memory:")
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        # Create HTTP session
        self.http_session = aiohttp.ClientSession()

        # Make DB connection
        self.db = await aiosqlite.connect(self.db_name, detect_types=1)
        # allow for name-based access of data columns
        self.db.row_factory = aiosqlite.Row

        self.boot_time = datetime.utcnow()

    async def close(self):
        """Subclass the close() method to close the HTTP Session."""

        await self.http_session.close()
        await self.db.close()
        await super().close()

    async def on_ready(self):
        permissions = discord.Permissions(permissions=67584)
        oauth_url = discord.utils.oauth_url(self.user.id, permissions=permissions)
        print(
            f"Logged in as {self.user.name} (ID:{self.user.id})\n"
            "--------\n"
            f"Current Discord.py Version: {discord.__version__}\n"
            "--------\n"
            f"Use this link to invite {self.user.name}:\n"
            f"{oauth_url}\n"
            "--------"
        )


async def main():
    intents = discord.Intents.all()
    allowed_mentions = discord.AllowedMentions(replied_user=False)

    bot = Zenyatta(
        description="One cannot survive on strength alone.",
        command_prefix="!",
        help_command=commands.DefaultHelpCommand(dm_help=False),
        intents=intents,
        allowed_mentions=allowed_mentions,
        db_name="db/Zenyatta.db",
    )

    startup_extensions = [
        "cogs.Admin",
        "cogs.Overwatch",
        "cogs.SeaofThieves",
        "cogs.General",
        "cogs.Fun",
    ]

    async with bot:
        for extension in startup_extensions:
            try:
                print(f"Loading extension {extension}... ", end="")
                await bot.load_extension(extension)
            except Exception as e:
                exc = "{}: {}".format(type(e).__name__, e)
                print("Failed to load extension {}\n{}".format(extension, exc))
            else:
                print("Extension loaded successfully.")
        await bot.start(config.token)


if __name__ == "__main__":
    asyncio.run(main())
