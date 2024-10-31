
class OtkDict(dict):
    def __init__(self, other: dict):
        self.otk_src = ""
        self.update(other)


class OtkList(list):
    def __init__(self, other: list):
        self.otk_src = ""
        self.extend(other)
        if isinstance(other, OtkList):
            self.otk_src = other.otk_src
    def replace(self, new: list):
        self.clear()
        self.extend(new)
