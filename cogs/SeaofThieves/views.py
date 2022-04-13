import itertools
import json
from pathlib import Path
import random

import discord
from discord import ButtonStyle
from discord.ui import View, Button


with open(Path(__file__).parent / "chat_wheel.json") as f:
    CHAT_WHEEL = json.load(f)

SEA_OF_THEIVES_EMOJI = discord.PartialEmoji.from_str(
    "<:sea_of_thieves:788880548369006603>"
)
EMBED_COLOR = 0x2C8C77
SHIP_THUMBNAILS = {
    0: "https://i.imgur.com/32ETrPN.png",  # rowboat
    1: "https://i.imgur.com/jWLAncv.png",  # sloop
    2: "https://i.imgur.com/jWLAncv.png",  # sloop
    3: "https://i.imgur.com/SVuzVC9.png",  # brigantine
    4: "https://i.imgur.com/IUhCCSt.png",  # galleon
}


def random_chat_wheel():
    all_chat = itertools.chain.from_iterable(CHAT_WHEEL.values())
    valid_ends = (".", "!", "?", "*")
    valid_chats = set([x for x in all_chat if x.endswith(valid_ends)])
    return random.choice(list(valid_chats))


class YarrAddButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(
            style=ButtonStyle.blurple,
            emoji=SEA_OF_THEIVES_EMOJI,
            label="Aye aye cap'n!",
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.add_crewmate(interaction.user)
        await interaction.response.edit_message(embed=self.view.build_embed())


class YarrRemoveButton(Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.grey, label="Count me out...")

    async def callback(self, interaction: discord.Interaction):
        self.view.remove_crewmate(interaction.user)
        await interaction.response.edit_message(embed=self.view.build_embed())


class YarrView(View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=None)

        self.crew = {member}
        self._captain = member
        self.random_chat = random_chat_wheel()
        self.gif_url = None

        self.add_item(YarrAddButton())
        self.add_item(YarrRemoveButton())

    def add_crewmate(self, member: discord.Member):
        self.crew.add(member)

    def remove_crewmate(self, member: discord.Member):
        self.crew.discard(member)

    def build_embed(self, gif_url=None):
        """Build the Embed with the new data."""

        if gif_url and self.gif_url is None:
            self.gif_url = gif_url

        description = (
            f"**{self.random_chat}**\n"
            f"{self._captain.display_name} ({self._captain.mention}) "
            "sails today, join in on the plunder!"
        )

        crew_list = "\n".join([f"{m.display_name} ({m.mention})" for m in self.crew])

        embed = (
            discord.Embed(description=description, color=EMBED_COLOR)
            .set_image(url=self.gif_url)
            .set_thumbnail(url=SHIP_THUMBNAILS[min(len(self.crew), 4)])
            .add_field(name="Crew", value=crew_list if crew_list else "No matey")
        )

        return embed
