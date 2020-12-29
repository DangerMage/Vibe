import traceback

import toml

import bot.filters.filter_handler as fh
from bot.util.custom_dicts import DefaultDict

import bot as bot_global


class GlobalConfig(DefaultDict):
    """
    Handling configuration options for filtering and other custom things. Easier to handle in this class then another.
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
                    "log_type": "compact"
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
        self.log_type = fh.MessageType.compact
        self.ignores = []

    def update(self, update):
        super().update(update)
        # We need to setup specific variables for ease of use.
        self.channel = self.bot.get_channel(self.get("filter", "warn_message", "channel"))
        self.log_type = fh.MessageType[self.get("filter", "warn_message", "log_type")]
        ic = self.get("filter", "ignores_ci")
        ignores = self.get("filter", "ignores")
        filter_type = fh.FilterType[self.get("filter", "ignores_type")]
        if len(ignores) == 0:
            self.ignores = []
        else:
            self.ignores = []
            for i in ignores:
                try:
                    self.ignores.append(fh.FilterType.compile_regex(filter_type, i, ic))
                except Exception as e:
                    print(f"Could not setup regex for {i}. {e}")


class Loadable(object):

    subs = dict()

    def __init__(self):
        name = type(self).__name__
        Loadable.subs[name] = self

    def start_load(self):
        raise NotImplementedError

    def load(self, dictionary):
        raise NotImplementedError


class FileProcessor:
    """
    Processes files
    """

    @classmethod
    def load(cls):
        for l in Loadable.subs.values():
            l.start_load()
        # Get all toml files from directory.
        p = bot_global.rules_dir.glob("**/*.toml")
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
                    bot_global.custom_config.update(globes)
                    globe_found = True
                else:
                    print("You already declared globals! Don't do it again!")
            for l in Loadable.subs.values():
                l.load(tom)
