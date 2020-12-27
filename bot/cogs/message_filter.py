import re

from discord.ext import commands


class MessageFilter:

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author == self.bot.user:
            return


def setup(bot):
    bot.add_cog(MessageFilter(bot))
