import copy
from functools import partial
from typing import Optional

__all__ = [
    'exclude_from_dict',
    'find_data_by_next_key'
]

def exclude_from_dict(d: dict, excess_keys: list[str], ) -> dict:
    """Exclude (obscure) values from dict that contains keys path for every excess_keys"""
    new_d = copy.deepcopy(d)
    for full_key in excess_keys:
        keys = full_key.split('.')
        _do_exclude(keys, new_d)

    return new_d


def _do_exclude(keys: Optional[list[str]], d: Optional[dict]) -> None:
    """Exclude (obscure) values from d that contains passed keys path

        keys symbols meaning:
            _ -> any value for 1 level
            * -> any values from 0 to deepest level
            + -> any values from 1 to deepest level
            | -> keys separator (or alternative) for 1 level
    """
    if not d or not keys or not list(filter(lambda k: k != '_', keys)):
        return

    curr_key = keys[0]
    if len(keys) == 1:
        for key in curr_key.split('|'):
            if d.get(key):
                d[key] = '%'  # obscuring data

    else:
        shift = 1
        get_inner = None
        if curr_key == '_':
            while keys[shift:] == '_':
                shift += 1
            iter_keys = keys[shift].split('|')
            get_inner = partial(find_data_by_next_key, d=d, depth=shift)

        elif curr_key in '*+':
            iter_keys = keys[shift].split('|')
            get_inner = partial(find_data_by_next_key, d=d, depth=None)

        else:
            iter_keys = curr_key.split('|')

        inner = []
        for key in iter_keys:
            if not get_inner:
                val = d.get(key)
                if isinstance(val, list):
                    inner += val
                else:
                    inner += [val]
            else:
                inner += get_inner(next_key=key)

        if curr_key == '+' and d in inner:
            inner.remove(d)

        for value in inner:
            _do_exclude(keys[shift:], value)


def find_data_by_next_key(d: dict, next_key: str, depth: Optional[int]) -> list[dict]:
    """Getting all dicts that contains next_key in passed depth"""
    if depth is not None and depth < 0:
        return []

    next_depth = depth - 1 if depth is not None else None
    go_deeper = depth >= 0 if isinstance(depth, int) else True

    result = []
    for key, value in d.items():
        if go_deeper:
            if isinstance(value, dict):
                result += find_data_by_next_key(value, next_key, next_depth)

            elif isinstance(value, tuple) or isinstance(value, list):
                for inner in (inner for inner in value if isinstance(inner, dict)):
                    result += find_data_by_next_key(inner, next_key, next_depth)

        if (depth is None or depth == 0) and key == next_key:
            result += [d]

    return result

