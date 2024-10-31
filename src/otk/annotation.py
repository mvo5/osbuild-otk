
class OtkDict(dict):
    def __init__(self, other: dict):
        # XXX: this should be a dataclass
        self.otk_src = ""
        self.update(other)
