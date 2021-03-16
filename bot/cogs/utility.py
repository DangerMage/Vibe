from discord.ext import commands
import bot as bot_global
from bot.file_manager import FileProcessor
from discord.utils import get


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
        
    @commands.command(name="lockdown")
    @bot_global.bot_manager()
    async def reload_filters(self, ctx):
        """Locks down the server, no more !agree"""
        with open('./lockdown.txt', 'r+') as file:
            currentState = file.read()
            if currentState == '1': # Server is in lockdown
                file.seek(0) # Move cursor to start of file
                file.write('0') # Change lockdown to false
                file.truncate() # Finish writing to file
                await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True) # Disable lockdown
            elif currentState == '0': # Server is not in lockdown
                file.seek(0) # Move cursor to start of file
                file.write('1') # Change lockdown to true
                file.truncate() # Finish writing to file
                await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False) # Enable lockdown
            else: # File is not an expected value, send error to console
                print("Unexpected value in 'lockdown.txt' file. Received: " + currentState)
                
    @commands.command(name="agree")
    async def agree(self, ctx):
        if ctx.channel.id != 720394587792867378:
            return
        role = get(ctx.guild.roles, name="Verified")
        await ctx.author.add_roles(role)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Utility(bot))
