import discord
from discord.ext import commands

from . import menus


GRANDMASTER_ROLE_ID = [
    697122661825773709,  # @GrandMaster
    593836553470738432,  # @bro
]


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.has_any_role(*GRANDMASTER_ROLE_ID)
    async def create(self, ctx, category_name, role_name=None):
        """Create a category including a text and a voice channel,
        as well as a role, and give the necessary permissions.
        """
        if role_name is None:
            role_name = category_name

        text_channel_name = category_name.replace(" ", "-")
        voice_channel_name = category_name
        category_name = category_name.upper()

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
            color=discord.Color.blurple()
        )
        menu = menus.ConfirmMenu(embed=embed)
        confirmed = await menu.prompt(ctx)

        if confirmed:
            # get roles
            grandmaster_role = ctx.guild.get_role(GRANDMASTER_ROLE_ID)
            everyone = ctx.guild.default_role

            # create new role
            role = await ctx.guild.create_role(
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
            category = await ctx.guild.create_category_channel(
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
                f"and :speaker: {voice_channel.mention}! "
                "You might want to move the category in the channels list..."
            )

            await ctx.send(content)

    @create.error
    async def create_error(self, ctx, error):
        """Error handler for the create command."""

        if isinstance(error, (commands.NoPrivateMessage,
                              commands.BotMissingPermissions)):
            await ctx.send(error)

        elif isinstance(error, commands.MissingAnyRole):
            await ctx.send(
                "You are missing a required role to run this command.")

        else:
            raise error
