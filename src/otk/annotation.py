import json

from json import JSONEncoder
from typing import Any


class OtkNode:
    def __init__(self, value, otk_src=None):
        self.value = value
        if otk_src:
            # XXX: add a way to merge
            self._otk_src = otk_src
    
    @property
    def otk_src(self):
        return self._otk_src

    @otk_src.setter
    def otk_src(self, value):
        self._otk_src = value

    # needed so that we can compare things in dicts
    def __eq__(self, other):
        if isinstance(other, OtkNode):
            return self.value == other.value
        return self.value == other

    # needed so that we can put things into dicts
    def __hash__(self):
        return hash(self.value)


# needed so that yaml loading "feels" natural
class OtkDict(OtkNode):
    def __getitem__(self, item):
        return self.value.__getitem__(item)


# needed so that yaml loading "feels" natural
class OtkList(OtkNode):
    def __getitem__(self, item):
        return self.value.__getitem__(item)


def otk_deep_convert(data):
    ret = data
    if isinstance(data, OtkNode):
        return ret
    if isinstance(data, dict):
        ret = OtkDict({
            key: otk_deep_convert(value) for key, value in data.items()
        })
    elif isinstance(data, list):
        ret = OtkList([otk_deep_convert(item) for item in data])
    elif isinstance(data, str):
        ret = OtkStr(data)
    elif isinstance(data, int):
        ret = OtkInt(data)


# this is needed for the external data which does not come in via
# the yaml loader
def otk_deep_convert_from(origin: OtkNode, data: Any):
    ret = data
    if isinstance(data, OtkNode):
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
