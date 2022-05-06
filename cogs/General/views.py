import discord
from discord import ui


class Confirm(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confirmed = None

    @ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def on_confirm(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Confirming", ephemeral=True)
        self.confirmed = True
        self.stop()

    @ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def on_cancel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.confirmed = False
        self.stop()
