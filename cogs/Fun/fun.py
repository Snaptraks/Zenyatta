import io
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

import config


COG_PATH = Path(__file__).parent


class Fun(commands.Cog):
    """Collection of useless but fun commands."""

    def __init__(self, bot):
        self.bot = bot

        self.bonk_context = app_commands.ContextMenu(
            name="Bonk", callback=self._bonk_context, guild_ids=[config.dev_guild.id]
        )
        self.bot.tree.add_command(self.bonk_context)

    @commands.hybrid_command(name="bonk")
    @app_commands.describe(text="Text to add to the image")
    @app_commands.guilds(config.dev_guild)
    async def bonk_command(self, ctx, member: discord.Member, *, text: str = None):
        """Bonk a member, and add a message!
        Due to the member argument not being last, you will have to
        use a mention (@User Here) or quote "User Here" their name
        if it contains spaces.
        """

        await ctx.reply(file=await self.create_bonk_file(member, text))

    @bonk_command.error
    async def bonk_error(self, ctx, error):
        """Error handler for the bonk command."""

        if isinstance(
            error, (commands.MemberNotFound, commands.MissingRequiredArgument)
        ):
            await ctx.reply(error)

        else:
            raise error

    async def _bonk_context(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        """Bonk a member!"""

        await interaction.response.send_message(
            file=await self.create_bonk_file(member, None)
        )

    async def create_bonk_file(self, member, text=None):
        """Common funtion to fetch the member avatar, and create the file to send."""

        avatar = io.BytesIO(await member.display_avatar.read())
        bytes = await self.bot.loop.run_in_executor(
            None, self._assemble_bonk_image, avatar, text
        )
        return discord.File(bytes, filename="bonk.png")

    def _assemble_bonk_image(self, avatar_bytes, text=None):
        avatar = Image.open(avatar_bytes)
        template = Image.open(COG_PATH / "bonk_template.png")

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
