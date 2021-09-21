import itertools
import json
import os
import random

import discord
from discord.ext import commands, menus
from ..utils.gifs import random_gif


COG_PATH = os.path.dirname(__file__)

with open(os.path.join(COG_PATH, "chat_wheel.json")) as f:
    CHAT_WHEEL = json.load(f)

SEA_OF_THEIVES_EMOJI = "<:sea_of_thieves:788880548369006603>"
SKULL = "\N{SKULL AND CROSSBONES}"
EMBED_COLOR = 0x2C8C77
SHIP_THUMBNAILS = {
    0: "https://i.imgur.com/32ETrPN.png",  # rowboat
    1: "https://i.imgur.com/jWLAncv.png",  # sloop
    2: "https://i.imgur.com/jWLAncv.png",  # sloop
    3: "https://i.imgur.com/SVuzVC9.png",  # brigantine
    4: "https://i.imgur.com/IUhCCSt.png",  # galleon
}


class YarrMenu(menus.Menu):
    """Menu to confirm if you're going to play Sea of Thieves."""

    def __init__(self, *args, **kwargs):
        self.pirate_role = kwargs.pop("pirate_role")
        super().__init__(*args, **kwargs)
        self.crew = set()

    async def send_initial_message(self, ctx, channel):

        self.gif_url = await random_gif(self.bot.http_session, "sea of thieves")

        all_chat = itertools.chain.from_iterable(CHAT_WHEEL.values())
        valid_ends = (".", "!", "?", "*")
        valid_chats = set([x for x in all_chat if x.endswith(valid_ends)])
        if ctx.author.id == 242465567259230208:  # Elerinna
            self.random_chat = f":rainbow: {CHAT_WHEEL['alerts'][-1]}"
        else:
            self.random_chat = random.choice(list(valid_chats))

        embed = await self.build_embed()
        return await channel.send(
            content=self.pirate_role.mention,
            embed=embed,
        )

    @menus.button(SEA_OF_THEIVES_EMOJI)
    async def on_confirm(self, payload):
        """Register for the Sea of Thieves session."""

        member = payload.member
        if member is None:
            member = self.bot.get_user(payload.user_id)

        if member in self.crew:
            self.crew.remove(member)
        else:
            self.crew.add(member)

        await self.update_page()

    async def update_page(self):
        """Rebuild the Embed with the new data."""

        embed = await self.build_embed()
        await self.message.edit(embed=embed)

    async def build_embed(self):
        """Build the Embed with the new data."""

        description = (
            f"**{self.random_chat}**\n"
            f"{self.ctx.author.display_name} ({self.ctx.author.mention}) "
            "sails today, join in on the plunder!"
        )

        crew_list = "\n".join([f"{m.display_name} ({m.mention})"
                               for m in self.crew])

        converter = commands.EmojiConverter()
        emoji = await converter.convert(self.ctx, SEA_OF_THEIVES_EMOJI)

        embed = discord.Embed(
            description=description,
            color=EMBED_COLOR,
        ).set_image(
            url=self.gif_url,
        ).set_thumbnail(
            url=SHIP_THUMBNAILS[min(len(self.crew), 4)],
        ).add_field(
            name="Crew",
            value=crew_list if crew_list else "No matey",
        ).set_footer(
            text="React to confirm your presence.",
            icon_url=emoji.url,
        )

        return embed

    def reaction_check(self, payload):
        """Override the function to allow for everyone to react."""

        if payload.message_id != self.message.id:
            return False

        if payload.user_id == self.bot.user.id:
            return False

        return payload.emoji in self.buttons
