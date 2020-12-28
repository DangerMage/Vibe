from discord.ext import commands
import bot as bot_global


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="filtered")
    @commands.is_owner()
    async def filtered_list(self, ctx):
        message = '\n'.join([p for p in bot_global.main_filter.filters])
        await ctx.send(message)

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload_filters(self, ctx):
        bot_global.main_filter.load()
        await ctx.send("Loaded!")


def setup(bot):
    bot.add_cog(Utility(bot))
