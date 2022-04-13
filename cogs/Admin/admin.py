from discord.ext import commands

import config


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.group(invoke_without_command=True)
    async def sync(self, ctx):
        """Sync AppCommands to Discord."""

        await ctx.send_help(ctx.command)

    @sync.command(name="dev")
    async def sync_dev(self, ctx):
        """Sync development AppCommands to Discord."""

        await self.bot.tree.sync(guild=config.dev_guild)
        await ctx.reply("Syncing to dev guild successful.")

    @sync.command(name="all")
    async def sync_all(self, ctx):
        """Sync all AppCommands to Discord."""
        await self.bot.tree.sync()
        await ctx.reply("Syncing all AppCommands successful.")
