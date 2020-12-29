import pathlib
import re
import enum

import discord

import bot.file_manager as fm
import bot.filters.basic_filter as basic
import bot as bot_global


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
            config = bot_global.custom_config
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


class FilterType(enum.Enum):

    regex = 0
    literal = 1

    @classmethod
    def compile_regex(cls, filter_type, input, ignore_case):
        if filter_type.value == FilterType.literal.value:
            input = re.escape(input)
        if ignore_case:
            return re.compile(input, flags=re.IGNORECASE)
        else:
            return re.compile(input)


class Filtered:
    """
    Used to store results of a successful filter.
    """

    __slots__ = ('original', 'problems')

    def __init__(self, original, problems):
        self.original = original
        self.problems = problems


class FilterHandler(fm.Loadable):

    def __init__(self, bot):
        super().__init__()
        self.rules_dir = pathlib.Path("./rules")
        self.filters = None
        self.bot = bot

    def filter_message(self, message):
        """
        Filters a message through all of the filters.
        """
        true_matches = []
        for i in bot_global.custom_config.ignores:
            message = re.sub(i, "", message)
        for i in range(1, 6):
            for filt in self.filters[i]:
                matches = filt.filter_message(message)
                if len(matches) > 0:
                    true_matches.extend(filt.filter_message(message))
                    # We already found a trigger so if we don't want to find all, we can stop.
                    if not bot_global.custom_config.get("filter", "find_all"):
                        break

        if len(true_matches) == 0:
            return None

        return true_matches

    def start_load(self):
        self.filters = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: []
        }

    def load(self, tom):
        # Default filter options for the files.
        filter_defaults = tom.get('filter_defaults', {})
        d_search_text = filter_defaults.get('search_text', '')
        d_search_type = FilterType[filter_defaults.get('search_type', 'regex')]
        d_search_ci = filter_defaults.get('search_ci', False)
        d_ignore_text = filter_defaults.get('ignore_text', '')
        d_ignore_type = FilterType[filter_defaults.get('ignore_type', 'literal')]
        d_ignore_ci = filter_defaults.get('ignore_ci', False)
        d_priority = filter_defaults.get('priority', 3)
        # -----
        filts = tom.get('filter', {})

        for filt in filts:
            try:
                priority = filt.get('priority', d_priority)
                if priority not in self.filters:
                    raise ValueError(f"Priority has to be an int between 1 and 5! Filter: f{filt.get('search_text', d_search_text)}")
                self.filters[priority].append(
                    basic.BasicFilter(filt.get('search_text', d_search_text),
                                FilterType[filt.get('search_type', d_search_type.name).lower()],
                                filt.get('search_ci', d_search_ci),
                                filt.get('ignore_text', d_ignore_text),
                                FilterType[filt.get('ignore_type', d_ignore_type.name).lower()],
                                filt.get('ignore_ci', d_ignore_ci)
                                )
                )
            except Exception as e:
                print(f"Could not load filter {filt.get('search_text', d_search_text)}. {e}")
