from discord.ext import commands
import bot as bot_global


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="filtered")
    @commands.is_owner()
    async def filtered_list(self, ctx):
        message = '\n'.join([p.pattern for p in bot_global.main_filter.filter_regex])
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Utility(bot))
