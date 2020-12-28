import pathlib
import re
import traceback
import toml
import enum

from bot.filters.basic_filter import BasicFilter
from bot.util.custom_dicts import DefaultDict


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


class GlobalConfig(DefaultDict):
    """
    Handling configuration options for filtering. Easier to handle in this class then another.
    """

    @property
    def defaults(self):
        return {
            "filter": {
                "find_all": True,
                "warn_message": {
                    "footer": "If you believe this was a mistake, please contact a staff member.",
                    "text": "Hey! I found an inappropriate word in your message. Please be a bit nicer :)"
                            "\n\n**Original Message**"
                            "\n{original}"
                            "\n\n**Trigger Word(s)**"
                            "\n{triggers}",
                    "title": "You triggered the filter!",
                    "channel": 0,
                },
                "ignores_ci": True,
                "ignores": [],
                "ignores_type": "literal"
            }
        }

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.channel = None
        self.ignores = []

    def update(self, update):
        super().update(update)
        self.channel = self.bot.get_channel(self.get("filter", "warn_message", "channel"))
        ic = self.get("filter", "ignores_ci")
        ignores = self.get("filter", "ignores")
        is_regex = FilterType[self.get("filter", "ignores_type")] == FilterType.regex
        if len(ignores) == 0:
            self.ignores = []
        else:
            self.ignores = []
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
        self.config = GlobalConfig(bot)
        self.bot = bot
        self.load()

    def filter_message(self, message):
        true_matches = []
        for i in self.config.ignores:
            message = re.sub(i, "", message)
        for i in range(1, 6):
            for filt in self.filters[i]:
                matches = filt.filter_message(message)
                if len(matches) > 0:
                    true_matches.extend(filt.filter_message(message))
                    # We already found a trigger so if we don't want to find all, we can stop.
                    if not self.config.get("filter", "find_all"):
                        break

        if len(true_matches) == 0:
            return None

        return true_matches

    def load(self):
        self.filters = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: []
        }

        # Get all toml files from directory.
        p = self.rules_dir.glob("**/*.toml")
        files = [x for x in p if x.is_file()]

        # We only want one global configuration place. Makes it easy to
        # do quick changes for filters and configurable stuff.
        globe_found = False
        for f in files:
            print(f"Loading file: {str(f)}")
            try:
                data = f.read_text()
                tom = toml.loads(data)
            except Exception:
                traceback.print_exc()
                continue
            globes = tom.get('globals')
            if globes is not None:
                if not globe_found:
                    self.config.update(globes)
                    globe_found = True
                else:
                    print("You already declared globals! Don't do it again!")

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
                        BasicFilter(filt.get('search_text', d_search_text),
                                    FilterType[filt.get('search_type', d_search_type.name).lower()],
                                    filt.get('search_ci', d_search_ci),
                                    filt.get('ignore_text', d_ignore_text),
                                    FilterType[filt.get('ignore_type', d_ignore_type.name).lower()],
                                    filt.get('ignore_ci', d_ignore_ci)
                                    )
                    )
                except Exception as e:
                    print(f"Could not load filter {filt.get('search_text', d_search_text)}. {e}")
