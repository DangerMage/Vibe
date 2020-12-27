import traceback
from datetime import datetime
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
        bot.config = Config("config.json")
        bot.main_filter = FilterHandler()

        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)

        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents, description=description,
                         case_insensitive=True, owner_id=523605852557672449, allowed_mentions=allowed_mentions)
        self.boot = datetime.now()

        for extension in startup_extensions:
            try:
                self.load_extension(cogs_dir + "." + extension)

            except (discord.ClientException, ModuleNotFoundError):
                print(f'Failed to load extension {extension}.')
                traceback.print_exc()

    def run(self):
        super().run(bot.config['bot_token'], reconnect=True, bot=True)

    async def on_ready(self):
        print("Bot up and running!")
