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

        await self._poll_callback(interaction, max_values=1)

    @poll.command(name="multiple")
    async def poll_multiple(
        self,
        interaction: discord.Interaction,
        max_answers: app_commands.Range[int, 2, 25] = 25,
    ):
        """Create a multiple choice poll."""

        await self._poll_callback(interaction, max_values=max_answers)

    async def _poll_callback(
        self, interaction: discord.Interaction, *, max_values: int
    ):
        """Callback for poll creation and sending to the channel."""

        modal = views.PollCreate()
        await interaction.response.send_modal(modal)
        await modal.wait()

        options = modal.options.value.split("\n")
        max_values = min(max_values, len(options))

        view = views.PollInput(
            author=interaction.user, modal=modal, max_values=max_values
        )
        embed, graph = await view.build_embed()

        await interaction.followup.send(
            embed=embed, file=graph, view=view,
        )
