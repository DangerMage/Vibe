import re


class BaseFilter:

    def filter_message(self, message):
        raise NotImplementedError()


class BasicFilter(BaseFilter):

    __slots__ = ('search', 'ignore')

    def __init__(self, search_text, search_regex, search_ci, ignore_text, ignore_regex, ignore_ci):
        if not isinstance(search_ci, bool):
            raise ValueError("Search Ignore Case must be a boolean")
        if not isinstance(ignore_ci, bool):
            raise ValueError("Ignore Ignore Case must be a boolean")
        if search_text is None or len(search_text) == 0:
            raise ValueError("Search text has to exist!")
        if not search_regex:
            search_text = re.escape(search_text)
        if search_ci:
            self.search = re.compile(search_text, flags=re.IGNORECASE)
        else:
            self.search = re.compile(search_text)
        if ignore_text is None or len(ignore_text) == 0:
            self.ignore = None
            return

        if isinstance(ignore_text, list):
            to_add = []
            for ig in ignore_text:
                if not ignore_regex:
                    irrex = re.escape(ig)
                else:
                    irrex = ignore_text
                if search_ci:
                    to_add.append(re.compile(irrex, flags=re.IGNORECASE))
                else:
                    to_add.append(re.compile(irrex))
            self.ignore = to_add
        else:
            if not ignore_regex:
                ignore_text = re.escape(ignore_text)
            if ignore_ci:
                self.ignore = [re.compile(ignore_text, flags=re.IGNORECASE)]
            else:
                self.ignore = [re.compile(ignore_text)]

    def filter_message(self, message):
        true_matches = []
        if self.ignore is not None:
            for i in self.ignore:
                # Remove bypassed words from the input.
                message = re.sub(i, '', message)

        matches = re.findall(self.search, message)
        for found in matches:
            if not isinstance(found, tuple):
                found = [found]
            for f in found:
                if f is None:
                    continue
                true_matches.append(f)
        return true_matches

    def __str__(self):
        return f"{self.search.pattern} - {self.ignore}"
