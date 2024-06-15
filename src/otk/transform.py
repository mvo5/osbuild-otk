"""To transform trees `otk` recursively modifies them. Trees are visited depth
first from left-to-right (top-to-bottom in omnifests).

Each type we can encounter in the tree has its own resolver. For many types
this would be the `dont_resolve`-resolver which leaves the value as is. For
collection types we want to recursively resolve the elements of the collection.

In the dictionary case we apply our directives. Directives are based on the
keys in the dictionaries."""

import logging
import pathlib
from typing import Any, Type

from .constant import (
    NAME_VERSION,
    PREFIX_DEFINE,
    PREFIX_OP,
    PREFIX_TARGET,
)
from .context import Context, OSBuildContext
from .directive import desugar, include, op
from .external import call

log = logging.getLogger(__name__)


def resolve(ctx: Context, tree: Any, path: pathlib.Path) -> Any:
    """Resolves a (sub)tree of any type into a new tree. Each type has its own
    specific handler to rewrite the tree."""

    # tree = copy.deepcopy(tree)

    typ = type(tree)
    if typ == dict:
        return resolve_dict(ctx, tree, path)
    elif typ == list:
        return resolve_list(ctx, tree, path)
    elif typ == str:
        return resolve_str(ctx, tree, path)
    elif typ in [int, float, bool, type(None)]:
        return tree
    else:
        log.fatal("could not look up %r in resolvers", type(tree))
        raise Exception(type(tree))


def resolve_dict(ctx: Context, tree: dict[str, Any], path) -> Any:
    for key in list(tree.keys()):
        val = tree[key]
        if key.startswith("otk."):
            if key.startswith("otk.define"):
                define(ctx, val, path)
                del tree[key]
            elif key == "otk.version":
                pass
            elif key.startswith("otk.target"):
                pass
            elif key.startswith("otk.include"):
                del tree[key]
                new_val, path = include(ctx, val, path)
                tree.update(resolve(ctx, new_val, path))
            elif key.startswith("otk.op"):
                tree.update(resolve(ctx, op(ctx, resolve(ctx, val), key), path))
            elif key.startswith("otk.external."):
                tree.update(resolve(ctx, call(key, resolve(ctx, val)), path))
            else:
                log.error("unknown directive %r %r:%r", key, tree, ctx)
                return tree
        else:
            tree[key] = resolve(ctx, val, path)
    return tree


def resolve_list(ctx, tree: list[Any], path: pathlib.Path) -> list[Any]:
    """Resolving a list means applying the resolve function to each element in
    the list."""
    log.debug("resolving list %r", tree)
    return [resolve(ctx, val, path) for val in tree]


def resolve_str(ctx, tree: str, path: pathlib.Path) -> Any:
    """Resolving strings means they are parsed for any variable
    interpolation."""
    log.debug("resolving str %r", tree)
    return desugar(ctx, tree)


#@tree.must_be(dict)
def define(ctx: Context, tree: Any, path: pathlib.Path) -> Any:
    """Takes an `otk.define` block (which must be a dictionary and registers
    everything in it as variables in the context."""

    for key, value in tree.items():
        ctx.define(key, resolve(ctx, value, path))

    return tree
