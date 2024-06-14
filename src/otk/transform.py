"""To transform trees `otk` recursively modifies them. Trees are visited depth
first from left-to-right (top-to-bottom in omnifests).

Each type we can encounter in the tree has its own resolver. For many types
this would be the `dont_resolve`-resolver which leaves the value as is. For
collection types we want to recursively resolve the elements of the collection.

In the dictionary case we apply our directives. Directives are based on the
keys in the dictionaries."""

import logging
import pathlib
import yaml
from dataclasses import dataclass
from typing import Any, Type

from .constant import (
    NAME_VERSION,
    PREFIX_DEFINE,
    PREFIX_OP,
    PREFIX_TARGET,
)
from .context import Context, OSBuildContext
from .directive import define, desugar,  op
from .external import call

log = logging.getLogger(__name__)


@dataclass
class ParserState:
    path: str
    in_define: bool


def resolve(ctx: Context, tree: Any, state: ParserState) -> Any:
    """Resolves a (sub)tree of any type into a new tree. Each type has its own
    specific handler to rewrite the tree."""

    # tree = copy.deepcopy(tree)

    typ = type(tree)
    if typ == dict:
        return resolve_dict(ctx, tree, state)
    elif typ == list:
        return resolve_list(ctx, tree, state)
    elif typ == str:
        return resolve_str(ctx, tree, state)
    elif typ in [int, float, bool, type(None)]:
        return tree
    else:
        log.fatal("could not look up %r in resolvers", type(tree))
        raise Exception(type(tree))


def resolve_dict(ctx: Context, tree: dict[str, Any], state: ParserState) -> Any:
    for key in list(tree.keys()):
        val = tree[key]
        if key.startswith("otk."):
            if key.startswith("otk.define"):
                new_state = ParserState(path=state.path, in_include=True)
                tree.update(resolve(ctx, define(ctx, val), new_state))
            elif key == "otk.version":
                pass
            elif key.startswith("otk.target"):
                pass
            elif key.startswith("otk.include"):
                del tree[key]
                new_val, new_path = include(ctx, val, state)
                new_state = copy.copy(state)
                new_state.path = new_path
                tree.update(resolve(ctx, new_val, new_state))
            elif key.startswith("otk.op"):
                tree.update(resolve(ctx, op(ctx, resolve(ctx, val), key), state))
            elif key.startswith("otk.external."):
                tree.update(resolve(ctx, call(key, resolve(ctx, val, state))))
            else:
                log.error("unknown directive %r %r:%r", key, tree, ctx)
                return tree
        else:
            if state.in_define:
                define(key, val)
            tree[key] = resolve(ctx, val, state)
    return tree


def resolve_list(ctx, tree: list[Any], state: ParserState) -> list[Any]:
    """Resolving a list means applying the resolve function to each element in
    the list."""
    log.debug("resolving list %r", tree)
    return [resolve(ctx, val, state) for val in tree]


def resolve_str(ctx, tree: str, state: ParserState) -> Any:
    """Resolving strings means they are parsed for any variable
    interpolation."""
    log.debug("resolving str %r", tree)
    return desugar(ctx, tree)


#@tree.must_be(str)
def include(ctx: Context, tree: Any, state: ParserState) -> (Any, pathlib.Path):
    """Include a separate file."""
    tree = resolve(ctx, tree, state)
    file = path / pathlib.Path(tree)

    # TODO str'ed for json log, lets add a serializer for posixpath
    # TODO instead
    log.info("otk.include=%s", str(file))

    # TODO
    return yaml.safe_load(file.read_text()), file.parent
