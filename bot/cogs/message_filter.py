import discord
from discord.ext import commands
import bot as bot_global


class MessageFilter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author == self.bot.user:
            return
        await self.filter_message(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.guild is None or after.author == self.bot.user:
            return
        await self.filter_message(after)

    async def filter_message(self, message):
        filtered = bot_global.main_filter.filter_message(message.clean_content)
        if filtered is None:
            return

        try:
            await message.delete()
        except Exception:
            pass

        if len(message.clean_content) > 1000:
            human = message[:1000]
        else:
            human = message.clean_content
        human.replace(r"{original}", "!original!")
        human.replace(r"{triggers}", "!triggers!")
        problems = '\n'.join(filtered)
        config = bot_global.main_filter.config
        embed = discord.Embed(
            title=config.get("filter", "warn_message", "title"),
            description=config.get("filter", "warn_message", "text").replace(r"{original}", human).replace(r"{triggers}", problems),
            colour=discord.Colour.red()
        )
        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
        embed.set_footer(text=config.get("filter", "warn_message", "footer"))
        try:
            await message.author.send(embed=embed)
        except Exception:
            pass
        try:
            channel = config.channel
            if channel is not None:
                await channel.send(embed=embed)
        except Exception:
            pass


def setup(bot):
    bot.add_cog(MessageFilter(bot))
