import logging

import discord
from discord.ext import commands
from discord import app_commands
from snapcogs.utils.views import confirm_prompt

LOGGER = logging.getLogger(__name__)


GRANDMASTER_ROLE_ID = [
    697122661825773709,  # @GrandMaster
    593836553470738432,  # @bro
]


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.bot_has_permissions(manage_channels=True, manage_roles=True)
    @app_commands.default_permissions(manage_channels=True)
    async def create(
        self, interaction: discord.Interaction, game_name: str, role_name: str = None
    ):
        """Make a category of channels for a game.

        Create a category including a text and a voice channel,
        as well as a role, and give the necessary permissions.
        """
        if role_name is None:
            role_name = game_name

        text_channel_name = game_name.replace(" ", "-")
        voice_channel_name = game_name
        category_name = game_name.upper()

        # ask to confirm first
        embed = discord.Embed(
            title="Category Creation Confirmation",
            description=(
                f"This will create a category **{category_name}**\n"
                f"with a text channel **#{text_channel_name}**,\n"
                f"a voice channel :speaker: **{voice_channel_name}**\n"
                f"and a role **@{role_name}**.\n"
                "Is this what you want?"
            ),
            color=discord.Color.blurple(),
        )

        confirm = await confirm_prompt(interaction, content=embed.description)

        if confirm:
            guild = interaction.guild
            # get roles
            for role_id in GRANDMASTER_ROLE_ID:
                grandmaster_role = interaction.guild.get_role(role_id)
                if grandmaster_role is not None:
                    break
            everyone = guild.default_role

            # create new role
            role = await guild.create_role(
                name=role_name,
                mentionable=True,
            )

            # create permissions
            overwrites = {
                grandmaster_role: discord.PermissionOverwrite(
                    read_messages=True,
                ),
                role: discord.PermissionOverwrite(
                    read_messages=True,
                ),
                everyone: discord.PermissionOverwrite(
                    read_messages=False,
                ),
            }

            # create the category
            category = await guild.create_category_channel(
                category_name,
                overwrites=overwrites,
            )

            # create the channels
            text_channel = await category.create_text_channel(
                text_channel_name,
            )
            voice_channel = await category.create_voice_channel(
                voice_channel_name,
            )

            content = (
                f"Done! See you in {text_channel.mention} "
                f"and {voice_channel.mention}! "
                "You might want to move the category in the channels list..."
            )

            await interaction.followup.send(content)

    @create.error
    async def create_error(self, ctx, error):
        """Error handler for the create command."""

        if isinstance(error, app_commands.BotMissingPermissions):
            await ctx.send(error)

        else:
            LOGGER.error(error, exc_info=error)
