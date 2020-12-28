import traceback
from datetime import datetime
from pathlib import Path

from discord.ext import commands

import discord

import bot
from bot.filters.filter_handler import FilterHandler
from bot.util.config import Config

description = """
The ultimate chat control discord bot.
"""

cogs_dir = "bot.cogs"

startup_extensions = ["message_filter", "utility"]


class VibeBot(commands.Bot):

    def __init__(self):
        print("Loading bot...")
        bot.config = Config(Path("./config.toml"))

        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)

        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix=bot.config['bot_prefix'], intents=intents, description=description,
                         case_insensitive=True, owner_id=bot.config['owner_id'], allowed_mentions=allowed_mentions)
        self.boot = datetime.now()

        for extension in startup_extensions:
            try:
                self.load_extension(cogs_dir + "." + extension)

            except (discord.ClientException, ModuleNotFoundError):
                print(f'Failed to load extension {extension}.')
                traceback.print_exc()

    def run(self):
        super().run(bot.config['bot_token'], reconnect=True, bot=True)
        bot.guild = self.get_guild(bot.config['bot_guild'])
        if bot.guild is not None:
            bot.manager_role = bot.guild.get_role(bot.config['bot_manager_role'])

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CheckFailure):
            return
        raise error

    async def on_ready(self):
        bot.main_filter = FilterHandler(self)
        print("Bot up and running!")
