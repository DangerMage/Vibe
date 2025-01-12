# Globals
# These are stuff that never should really change without our consent.
# For the config, it wouldn't make sense to have multiple, so we can store it here.
from pathlib import Path

from discord.ext import commands

config = None
main_filter = None
manager_role = None
guild = None
custom_config = None
rules_dir = Path("./rules")


def bot_manager():
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        if manager_role is not None:
            return manager_role in ctx.author.roles
        return False

    return commands.check(predicate)

async def is_bot_manager(author):
    if manager_role is not None:
        return manager_role in author.roles
    return False
