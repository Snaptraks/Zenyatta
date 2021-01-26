import io
import os

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont


COG_PATH = os.path.dirname(__file__)


class Fun(commands.Cog):
    """Collection of useless but fun commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bonk(self, ctx, member: discord.Member, *, text=None):
        """Bonk a member, and add a message!
        Due to the member argument not being last, you will have to
        use a mention (@User Here) or quote "User Here" their name
        if it contains spaces.
        """

        avatar_url = str(member.avatar_url_as(format="png"))
        async with self.bot.http_session.get(avatar_url) as resp:
            if resp.status == 200:
                avatar = io.BytesIO(await resp.content.read())
                avatar.seek(0)

        out = await self.bot.loop.run_in_executor(
            None, self.bonkify, avatar, text)

        await ctx.reply(file=discord.File(out, filename="bonk.png"))

    @bonk.error
    async def bonk_error(self, ctx, error):
        "Error handler for the bonk command."""

        if isinstance(error, (commands.MemberNotFound,
                              commands.MissingRequiredArgument)):
            await ctx.reply(error)

        else:
            raise error

    def bonkify(self, avatar_bytes, text=None):
        avatar = Image.open(avatar_bytes)
        template = Image.open(os.path.join(
            COG_PATH, "bonk_template.png"))

        new = Image.new("RGBA", template.size)

        # under the bat
        head = avatar.resize((200, 200), Image.ANTIALIAS)
        new.paste(head, (425, 235))

        new.paste(template, mask=template)

        if text is not None:
            # add text
            draw = ImageDraw.Draw(new)
            font = ImageFont.truetype("impact.ttf", 38)
            stroke_width = 2
            w, h = font.getsize(text, stroke_width=stroke_width)
            mx, my = (380, 60)  # middle
            x, y = mx - w // 2, my - h // 2

            draw.text(
                (x, y),
                text,
                font=font,
                fill=(255, 255, 255),
                stroke_width=stroke_width,
                stroke_fill=(0, 0, 0),
            )

        edited = io.BytesIO()
        new.save(edited, format="png")
        edited.seek(0)

        return edited
