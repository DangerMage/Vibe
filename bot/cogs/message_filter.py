import re

from discord.ext import commands


class MessageFilter:

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author == self.bot.user:
            return
        returnText = message.content
        text = message.content.lower()
        matches = re.search("(c+(\W|\d|_|)*r+(\W|\d|_)*a+(\W|\d|_)*p+(\W|\d|_)*)", text)

        bannedwords = ["crap", "shit", "fuck"]
        splitword = []
        for x in range(len(bannedwords)):
            word = bannedwords[x]
            for y in range(len(word)):
                splitword.append(word[y])

        if matches:
            await message.delete()
            await message.author.send(
                "Your message contained a word which we have blocked. Please modify it and try again")
            await message.author.send(returnText)


def setup(bot):
    bot.add_cog(MessageFilter(bot))
