import re

import bot.filters.filter_handler as handler


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
        self.search = handler.FilterType.compile_regex(search_regex, search_text, search_ci)
        if ignore_text is None or len(ignore_text) == 0:
            self.ignore = None
            return

        if isinstance(ignore_text, list):
            to_add = []
            for ig in ignore_text:
                to_add.append(handler.FilterType.compile_regex(ignore_regex, ig, ignore_ci))
            self.ignore = to_add
        else:
            self.ignore = [handler.FilterType.compile_regex(ignore_regex, ignore_text, ignore_ci)]

    def filter_message(self, message):
        # Sometimes with big ignore lists it can be more taxing to iterate through everything.
        if self.ignore is not None and len(re.findall(self.search, message)) == 0:
            return []
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
