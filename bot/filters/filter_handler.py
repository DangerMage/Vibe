import pathlib
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


class FilterHandler:

    def __init__(self):
        self.rules_dir = pathlib.Path("./rules")
        self.filters = None
        self.load()

    def filter(self, message):
        true_matches = []
        for filt in self.filters:
            true_matches.extend(filt.filter_message(message))

        if len(true_matches) == 0:
            return None

        return Filtered(message, true_matches)

    def load(self):
        self.filters = []
        # Get all toml files from directory.
        p = self.rules_dir.glob("**/*.toml")
        files = [x for x in p if x.is_file()]
        for f in files:
            print(f"Loading file: {str(f)}")
            try:
                data = f.read_text()
            except Exception:
                traceback.print_exc()
                continue
            tom = toml.loads(data)
            defaults = tom.get('defaults', {})
            # Defaults for the file
            d_search_text = defaults.get('search_text', '')
            d_search_type = FilterType[defaults.get('search_type', 'regex')]
            d_search_ci = defaults.get('search_ci', False)
            d_ignore_text = defaults.get('ignore_text', '')
            d_ignore_type = FilterType[defaults.get('ignore_type', 'literal')]
            d_ignore_ci = defaults.get('ignore_ci', False)

            for filt in tom['filter']:
                self.filters.append(
                    BasicFilter(filt.get('search_text', d_search_text),
                                FilterType[filt.get('search_type', d_search_type.name).lower()],
                                filt.get('search_ci', d_search_ci),
                                filt.get('ignore_text', d_ignore_text),
                                FilterType[filt.get('ignore_type', d_ignore_type.name).lower()],
                                filt.get('ignore_ci', d_ignore_ci)
                                )
                )
