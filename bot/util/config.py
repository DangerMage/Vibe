import json


class Config:

    def __init__(self, file: str):
        self.file = file
        self.data = {}
        self.loadfile()

    def loadfile(self):
        with open(file=self.file) as f:
            self.data = json.load(f)

    def save_file(self):
        with open(file=self.file, mode='w') as json_file:
            json.dump(self.data, json_file, indent=4, sort_keys=True)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save_file()

    def __contains__(self, item):
        return item in self.data
