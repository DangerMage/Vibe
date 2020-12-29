import discord
from discord.ext import commands
import bot as bot_global
import enum


class MessageType(enum.Enum):

    compact = 0
    compact_embed = 1
    embed = 2

    @classmethod
    def format_embed(cls, message_type, message, triggered):
        if message_type.value == MessageType.embed.value:
            if len(message.clean_content) > 1000:
                human = message.clean_content[:1000]
            else:
                human = message.clean_content
            human.replace(r"{original}", "!original!")
            human.replace(r"{triggers}", "!triggers!")
            problems = '\n'.join([t for t in triggered if len(t) != 1])
            config = bot_global.main_filter.config
            embed = discord.Embed(
                title=config.get("filter", "warn_message", "title"),
                description=config.get("filter", "warn_message", "text").replace(r"{original}", human).replace(
                    r"{triggers}", problems),
                colour=discord.Colour.red()
            )
            embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
            embed.set_footer(text=config.get("filter", "warn_message", "footer"))
            return embed
        if message_type.value == MessageType.compact.value:
            problems = '` '.join([t for t in triggered if len(t) != 1])
            human = message.clean_content
            if len(human) > 1200:
                human = human[:1200]
            return f"__Message from {message.author} triggered filter.__\nTriggered: `{problems}`\nOriginal: {human}"
        if message_type.value == MessageType.compact_embed.value:
            problems = '` '.join([t for t in triggered if len(t) != 1])
            human = message.clean_content
            if len(human) > 1200:
                human = human[:1200]
            embed = discord.Embed(
                text=f"__Message from {message.author} triggered filter.__\nTriggered: `{problems}`\nOriginal: {human}"
            )
            embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
            return embed
        return "Something went wrong"


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

        config = bot_global.main_filter.config
        try:
            await message.author.send(embed=MessageType.format_embed(MessageType.embed, message, filtered))
        except Exception:
            pass
        channel = config.channel
        if channel is not None:
            print(config.log_type.name)
            mes = MessageType.format_embed(config.log_type, message, filtered)
            if isinstance(mes, discord.Embed):
                await channel.send(embed=mes)
            else:
                await channel.send(mes)


def setup(bot):
    bot.add_cog(MessageFilter(bot))
