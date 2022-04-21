import discord
from discord import app_commands
from discord.ext import commands

from . import views

import config


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    poll = app_commands.Group(
        name="poll", description="Create a poll", guild_ids=[config.dev_guild.id]
    )

    @poll.command(name="single")
    async def poll_single(self, interaction: discord.Interaction):
        """Create a single choice poll."""

        modal = views.PollCreate()
        await interaction.response.send_modal(modal)
        await modal.wait()

        view = views.PollSingleInput(author=interaction.user, modal=modal)
        embed, graph = await view.build_embed()

        await interaction.followup.send(
            embed=embed, file=graph, view=view,
        )

    @poll.command(name="multiple")
    async def poll_multiple(
        self,
        interaction: discord.Interaction,
        max_values: app_commands.Range[int, 1, 25] = 25,
    ):
        """Create a multiple choice poll."""

        modal = views.PollCreate()
        await interaction.response.send_modal(modal)
        await modal.wait()

        options = modal.options.value.split("\n")
        max_values = min(max_values, len(options))
        view = views.PollMultipleInput(author=interaction.user, modal=modal)
        embed, graph = await view.build_embed()

        await interaction.followup.send(
            embed=embed, file=graph, view=view,
        )
