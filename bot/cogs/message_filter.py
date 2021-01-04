import discord
from discord.ext import commands
import bot as bot_global
import enum

from bot.filters.filter_handler import MessageType


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
        if message.author.id in bot_global.custom_config.bypassed:
            return
        if message.author.roles in bot_global.custom_config.bypassed:
            return
        filtered = bot_global.main_filter.filter_message(message.clean_content)
        if filtered is None:
            return

        try:
            await message.delete()
        except Exception:
            pass

        config = bot_global.custom_config
        try:
            await message.author.send(embed=MessageType.format_embed(MessageType.embed, message, filtered))
        except Exception:
            pass
        channel = config.channel
        if channel is not None:
            mes = MessageType.format_embed(config.log_type, message, filtered)
            if isinstance(mes, discord.Embed):
                await channel.send(embed=mes)
            else:
                await channel.send(mes)


def setup(bot):
    bot.add_cog(MessageFilter(bot))
