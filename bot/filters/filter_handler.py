import pathlib
import re
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

    def filter(self, message):
        true_matches = []
        for r in self.filter_regex:
            matches = re.search(r, message)
            if matches:
                for found in matches.group():
                    if found.lower() not in self.ignore:
                        true_matches.append(found)

        if len(true_matches) == 0:
            return None

        return Filtered(message, true_matches)

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
        for l in lines:
            try:
                l_regex = re.compile(l)
                self.filter_regex.append(l_regex)
            except Exception as e:
                print(f"Could not add regex: {l}\n\n{e}")
