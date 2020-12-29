from discord.ext import commands
import bot as bot_global
from bot.file_manager import FileProcessor


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="filtered")
    @bot_global.bot_manager()
    async def filtered_list(self, ctx):
        message = '\n'.join([p for p in bot_global.main_filter.filters])
        await ctx.send(message)

    @commands.command(name="reload")
    @bot_global.bot_manager()
    async def reload_filters(self, ctx):
        """Reloads filters"""
        FileProcessor.load()
        await ctx.send("Reloaded!")


def setup(bot):
    bot.add_cog(Utility(bot))
