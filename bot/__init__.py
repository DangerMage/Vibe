# Globals
# These are stuff that never should really change without our consent.
# For the config, it wouldn't make sense to have multiple, so we can store it here.
from discord.ext import commands

config = None
main_filter = None
manager_role = None
guild = None


def bot_manager():
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        if manager_role is not None:
            return manager_role in ctx.author.roles
        return False

    return commands.check(predicate)
