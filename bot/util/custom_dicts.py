class WalkableDict:

    def __init__(self, keys, value):
        self.keys = keys
        self.value = value

    def formatted(self):
        k = ': '.join(self.keys)
        return f"{k}: {self.value}"

    def items(self):
        return self.keys, self.value

    @classmethod
    def create_walkable(cls, dictionary, keys=None):
        if keys is None:
            keys = []
        for k, v in dictionary.items():
            if isinstance(v, dict):
                yield from cls.create_walkable(v, keys + [k])
            else:
                yield cls(keys + [k], v).items()


class DefaultDict:

    def __init__(self):
        self._data = self.defaults

    def get_dict(self):
        return self._data

    @property
    def defaults(self):
        raise NotImplementedError

    def update(self, update_dict):
        for keys, value in WalkableDict.create_walkable(self._data.copy()):
            try:
                current_data = self._data
                current_update = update_dict
                if len(keys) == 1:
                    current_data[keys[0]] = current_update[keys[0]]
                else:
                    dict_keys = keys[:-1]
                    for key in dict_keys:
                        current_data = current_data[key]
                        current_update = current_update[key]
                    current_data[keys[-1]] = current_update[keys[-1]]
            except KeyError:
                continue

    def get(self, *args):
        if len(args) == 1:
            try:
                return self._data[args[0]]
            except KeyError:
                return None
        nest = args[:-1]
        key = args[-1]
        current = self._data
        for item in nest:
            try:
                current = current[item]
            except:
                # Want to make this dumb dumb proof. Will just returndumb dumb proof. Will just return none.
                return None
        try:
            return current[key]
        except:
            return
