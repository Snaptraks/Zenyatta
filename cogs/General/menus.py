from discord.ext import menus


class ConfirmMenu(menus.Menu):
    """Menu that asks for confirmation before doing an action."""

    def __init__(self, *, content=None, embed=None):
        super().__init__(timeout=30.0, delete_message_after=True)
        self.content = content
        self.embed = embed
        self.result = None

    async def send_initial_message(self, ctx, channel):
        return await channel.send(content=self.content, embed=self.embed)

    @menus.button("\u2705")
    async def do_confirm(self, payload):
        self.result = True
        self.stop()

    @menus.button("\u274c")
    async def do_deny(self, payload):
        self.result = False
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait=True)
        return self.result
