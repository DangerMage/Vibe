import pathlib
import traceback


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
        self.ignore = []
        self.filter_regex = []
        self.load()

    def load(self):
        # Get all tet files from directory.
        p = self.rules_dir.glob("**/*.txt")
        files = [x for x in p if x.is_file()]
        for f in files:
            try:
                data = f.read_text()
            except Exception:
                traceback.print_exc()
                continue
            lines = data.split('\n')
            if "TYPE: IGNORE" in lines[0]:
                self.ignore_file(lines)
                continue
            if "TYPE: RULES":
                self.filter_file(lines)
                continue

    @classmethod
    def raw_lines(cls, lines):
        start = False
        new_lines = []
        for i, l in enumerate(lines):
            if not start:
                if "---" in l:
                    start = True
                continue
            if len(l) > 0 and l[0] != "#":
                new_lines.append(l)

        return new_lines

    def ignore_file(self, lines):
        lines = self.raw_lines(lines)
        if len(lines) == 0:
            return
        self.ignore.extend([l.lower() for l in lines])

    def filter_file(self, lines):
        lines = self.raw_lines(lines)
