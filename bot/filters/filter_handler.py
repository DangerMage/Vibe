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
        self.filter_regex_lower = []
        self.load()

    def filter(self, message):
        true_matches = []
        print(f"Searching {message}")
        true_matches.extend(self.search(message, self.filter_regex, self.ignore))
        true_matches.extend(self.search(message.lower(), self.filter_regex_lower, self.ignore))

        if len(true_matches) == 0:
            return None

        return Filtered(message, true_matches)

    def load(self):
        # Get all tet files from directory.
        p = self.rules_dir.glob("**/*.txt")
        files = [x for x in p if x.is_file()]
        for f in files:
            print(f"Loading file: {str(f)}")
            try:
                data = f.read_text()
            except Exception:
                traceback.print_exc()
                continue
            lines = data.split('\n')
            if "TYPE: IGNORE" in lines[0]:
                self.ignore_file(lines)
                continue
            if "TYPE: FILTER_REGEX_LOWER" in lines[0]:
                self.filter_file(lines, True)
                continue
            if "TYPE: FILTER_REGEX" in lines[0]:
                self.filter_file(lines, False)
                continue

    @classmethod
    def search(cls, message, regex_list, ignore):
        true_matches = []
        for r in regex_list:
            matches = re.findall(r, message)
            for found in matches:
                if not isinstance(found, tuple):
                    found = [found]
                for f in found:
                    if f is None:
                        continue
                    if f.lower() not in ignore:
                        true_matches.append(f)
        return true_matches

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

    def filter_file(self, lines, lower):
        lines = self.raw_lines(lines)
        for l in lines:
            try:
                l_regex = re.compile(l)
                if lower:
                    self.filter_regex_lower.append(l_regex)
                else:
                    self.filter_regex.append(l_regex)

            except Exception as e:
                print(f"Could not add regex: {l}\n\n{e}")
