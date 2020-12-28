"""
Run this file to initate the bot. Make sure you have setup the bot token in config.toml.
"""


from bot.vibe_bot import VibeBot


def run_bot():
    bot = VibeBot()
    bot.run()


if __name__ == '__main__':
    run_bot()
