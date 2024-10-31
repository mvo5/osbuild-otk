import json

from json import JSONEncoder
from typing import Any


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

    # XXX: not a good nameq
    def otk_dup(self, new: dict):
        new = OtkDict(new)
        new.otk_src = self.otk_src
        return new


class OtkList(OtkValueMixin, list):
    def __init__(self, other: list):
        self.extend(other)

    # XXX: not a good name
    def otk_dup(self, new: list):
        new = OtkList(new)
        new.otk_src = self.otk_src
        return new


class OtkStr(OtkValueMixin, str):
    def __new__(cls, other):
        val = super().__new__(cls, other)
        return val

    # XXX: not a good name
    def otk_dup(self, new):
        # str are immutable
        new = OtkStr(new)
        new.otk_src = self.otk_src
        return new


class OtkInt(OtkValueMixin, int):
    def __new__(cls, other):
        val = super().__new__(cls, other)
        return val


# bool can't be subclassed so we need to workaround
class OtkBool(OtkValueMixin):
    def __init__(self, other) -> None:
        self._bool = other


# this is only needed to support OtkBool
class OtkJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, OtkBool):
            return o._bool


# this is needed for the external data which does not come in via
# the yaml loader
def otk_deep_convert_from(origin: OtkValueMixin, data: Any):
    ret = data
    if isinstance(data, OtkValueMixin):
        return ret
    if isinstance(data, dict):
        ret = OtkDict({
            key: otk_deep_convert_from(origin, value)
            for key, value in data.items()
        })
    elif isinstance(data, list):
        ret = OtkList([
            otk_deep_convert_from(origin, item) for item in data
        ])
    elif isinstance(data, str):
        ret = OtkStr(data)
    # must be before int, because "isinstance(True, int) == True"
    elif isinstance(data, bool):
        ret = OtkBool(data)
    elif isinstance(data, int):
        ret = OtkInt(data)

    # None canot be subclasssed nor annotated :(
    if not ret is None:
        ret.otk_src = origin
    return ret
