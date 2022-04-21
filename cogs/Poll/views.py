import asyncio
from collections import Counter
import io

import discord
from discord import ui
import matplotlib.pyplot as plt


class PollCreate(ui.Modal, title="Poll Creation"):
    question = ui.TextInput(
        label="Question", placeholder="What do you want to ask about?", required=True
    )
    options = ui.TextInput(
        label="Options",
        placeholder="Enter one option per line (max 25)",
        required=True,
        style=discord.TextStyle.paragraph,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Poll created")


class PollSingleInput(ui.View):
    def __init__(self, *, author: discord.Member, modal: ui.Modal):
        super().__init__(timeout=None)
        self.author = author
        self.question = modal.question.value
        self.options = {}  # options to vote for
        self.results = {}  # what users voted for

        for i, option in enumerate(modal.options.value.split("\n")):
            value = str(i + 1)
            self.options[value] = option
            self.on_vote.add_option(label=option, value=value)

    @ui.select()
    async def on_vote(self, interaction: discord.Interaction, select: ui.Select):
        self.results[interaction.user.id] = select.values
        await self.update_message(interaction)

    @ui.button(label="Stop Poll", style=discord.ButtonStyle.red)
    async def on_stop(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id == self.author.id:
            await interaction.response.edit_message(view=None)
            self.stop()

        else:
            await interaction.response.send_message(
                "Only the poll author can stop the voting.", ephemeral=True
            )

    async def update_message(self, interaction):
        embed, graph = await self.build_embed()
        await interaction.response.edit_message(embed=embed, attachments=[graph])

    async def build_embed(self):
        description = "\n".join(
            f"`{i:>2}.` {option}" for i, option in self.options.items()
        )
        graph = await asyncio.get_running_loop().run_in_executor(None, self.build_graph)
        embed = discord.Embed(
            title=self.question, description=description, color=discord.Color.blurple()
        ).set_image(url=f"attachment://{graph.filename}")

        return embed, graph

    def build_graph(self):
        results = Counter([v for votes in self.results.values() for v in votes])
        labels = [
            f"{self.options[key]}\n({value} votes)" for key, value in results.items()
        ]

        fig, ax = plt.subplots()
        ax.pie(results.values(), labels=labels, wedgeprops={"width": 0.5})
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        plt.close(fig=fig)
        buffer.seek(0)

        return discord.File(buffer, "poll_results.png")


class PollMultipleInput(PollSingleInput):
    def __init__(self, *, author: discord.Member, modal: ui.Modal, max_values=None):
        super().__init__(author=author, modal=modal)
        self.on_vote.max_values = max_values or len(self.options)
