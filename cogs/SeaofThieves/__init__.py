from .seaofthieves import SeaofThieves


async def setup(bot):
    await bot.add_cog(SeaofThieves(bot))
