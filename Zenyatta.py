import aiosqlite
import aiohttp
from datetime import datetime
import discord
from discord.ext import commands

import config


async def create_http_session(loop):
    """Create an async HTTP session. Required to be from an async function
    by aiohttp>=3.5.4
    """
    return aiohttp.ClientSession(loop=loop)


async def create_db_connection(db_name):
    """Create the connection to the database."""

    return await aiosqlite.connect(
        db_name, detect_types=1)  # 1: parse declared types


class Zenyatta(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create HTTP session
        self.http_session = self.loop.run_until_complete(
            create_http_session(self.loop))

        # Make DB connection
        self.db = self.loop.run_until_complete(
            create_db_connection(kwargs.get('db_name', ':memory:')))
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
        oauth_url = discord.utils.oauth_url(
            self.user.id, permissions=permissions)
        print(
            f"Logged in as {self.user.name} (ID:{self.user.id})\n"
            "--------\n"
            f"Current Discord.py Version: {discord.__version__}\n"
            "--------\n"
            f"Use this link to invite {self.user.name}:\n"
            f"{oauth_url}\n"
            "--------"
        )


if __name__ == '__main__':
    intents = discord.Intents.all()

    bot = Zenyatta(
        description='One cannot survive on strength alone.',
        command_prefix='!',
        help_command=commands.DefaultHelpCommand(dm_help=False),
        intents=intents,
        db_name='db/Zenyatta.db',
    )

    startup_extensions = [
        "cogs.Overwatch",
        "cogs.SeaofThieves",
        "cogs.General",
        "cogs.Fun",
    ]

    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(config.token)
