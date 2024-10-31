
class OtkValueMixin:
    @property
    def otk_src(self):
        return self._otk_src

    @otk_src.setter
    def otk_src(self, value):
        self._otk_src = value


class OtkDict(OtkValueMixin, dict):
    def __init__(self, other: dict):
        self.update(other)


class OtkList(OtkValueMixin, list):
    def __init__(self, other: list):
        self.extend(other)
    def replace(self, new: list):
        self.clear()
        self.extend(new)


class OtkStr(OtkValueMixin, str):
   def __new__(cls, other):
        val = super().__new__(cls, other)
        return val


class OtkInt(OtkValueMixin, int):
   def __new__(cls, other):
        val = super().__new__(cls, other)
        return val
