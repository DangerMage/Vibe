import discord
from discord.ext import commands
import bot as bot_global


class MessageFilter:

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author == self.bot.user:
            return

        filtered = bot_global.main_filter.filter(message.clean_content)
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
        problems = '\n'.join(filtered.problems)
        embed = discord.Embed(
            title="Filtered word found in Message",
            description=f"Hey! I found an inappropriate word in your message. Your original message was:\n\n"
                        f"{human}\n\n**Trigger Word(s)**\n{problems}",
            colour=discord.Colour.red()
        )
        embed.set_footer(text="If you believe this was a mistake, please contact a staff member.")
        try:
            await message.author.send(embed=embed)
        except Exception:
            pass


def setup(bot):
    bot.add_cog(MessageFilter(bot))
