import pathlib
import re
import traceback
import toml
import enum

from bot.filters.basic_filter import BasicFilter


class FilterType(enum.Enum):

    regex = 0
    literal = 1


class Filtered:
    """
    Used to store results of a successful filter.
    """

    __slots__ = ('original', 'problems')

    def __init__(self, original, problems):
        self.original = original
        self.problems = problems


class FilterConfig:

    def __init__(self, bot):
        self.embed_footer = None
        self.embed_text = None
        self.embed_title = None
        self.channel = None
        self.ignores = []
        self.bot = bot
        self.find_all = True
        self.update_from_dict({})

    def update_from_dict(self, update):
        self.find_all = update.get('find_all', True)
        warn = update.get('warn_message', {})
        self.embed_footer = warn.get('footer', "If you believe this was a mistake, please contact a staff member.")
        self.embed_text = warn.get('text', "Hey! I found an inappropriate word in your message. Please be a bit nicer :) \
            **\n\nOriginal Message** \
            \n{original} \
            \n\n**Trigger Word(s)** \
            \n{triggers}")
        self.embed_title = warn.get('title', "You triggered the filter!")
        chan = warn.get('channel', 0)
        if chan == 0:
            self.channel = None
        else:
            self.channel = self.bot.get_channel(chan)
        ic = update.get("ignores_ci", True)
        ignores = update.get("ignores", [])
        is_regex = FilterType[update.get("ignores_type", "literal")] == FilterType.regex
        if len(ignores) == 0:
            self.ignores = []
        else:
            for i in ignores:
                try:
                    if not is_regex:
                        i = re.escape(i)
                    if ic:
                        self.ignores.append(re.compile(i, flags=re.IGNORECASE))
                    else:
                        self.ignores.append(re.compile(i))
                except Exception as e:
                    print(f"Could not setup regex for {i}. {e}")


class FilterHandler:

    def __init__(self, bot):
        self.rules_dir = pathlib.Path("./rules")
        self.filters = None
        self.config = FilterConfig(bot)
        self.bot = bot
        self.load()

    def filter(self, message):
        true_matches = []
        for i in self.config.ignores:
            message = re.sub(i, "", message)
        for filt in self.filters:
            matches = filt.filter_message(message)
            if len(matches) > 0:
                true_matches.extend(filt.filter_message(message))
                if not self.config.find_all:
                    break

        if len(true_matches) == 0:
            return None

        return Filtered(message, true_matches)

    def load(self):
        self.filters = []
        # Get all toml files from directory.
        p = self.rules_dir.glob("**/*.toml")
        files = [x for x in p if x.is_file()]
        globe_found = False
        for f in files:
            print(f"Loading file: {str(f)}")
            try:
                data = f.read_text()
            except Exception:
                traceback.print_exc()
                continue
            tom = toml.loads(data)
            globes = tom.get('globals')
            if globes is not None:
                if not globe_found:
                    self.config.update_from_dict(globes)
                    globe_found = True
                else:
                    print("You already declared globals! Don't do it again!")
            defaults = tom.get('defaults', {})
            # Defaults for the file
            d_search_text = defaults.get('search_text', '')
            d_search_type = FilterType[defaults.get('search_type', 'regex')]
            d_search_ci = defaults.get('search_ci', False)
            d_ignore_text = defaults.get('ignore_text', '')
            d_ignore_type = FilterType[defaults.get('ignore_type', 'literal')]
            d_ignore_ci = defaults.get('ignore_ci', False)
            filts = tom.get('filter', {})

            for filt in filts:
                self.filters.append(
                    BasicFilter(filt.get('search_text', d_search_text),
                                FilterType[filt.get('search_type', d_search_type.name).lower()],
                                filt.get('search_ci', d_search_ci),
                                filt.get('ignore_text', d_ignore_text),
                                FilterType[filt.get('ignore_type', d_ignore_type.name).lower()],
                                filt.get('ignore_ci', d_ignore_ci)
                                )
                )
