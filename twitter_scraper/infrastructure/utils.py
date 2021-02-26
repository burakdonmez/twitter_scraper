import functools
from typing import Generator, Sequence


def enforce_sequence(obj):
    if isinstance(obj, str) or (not isinstance(obj, Sequence) and not isinstance(obj, Generator)):
        return (obj,)
    return obj


def get_list(dict_item, keys):
    """Extracts a list from given dictionary.
    >>>get_list({'a':{'b': {'c': 'value',}}},['a', 'b', 'list'])
    []
    >>> get_list({'a':{'b': {'c': 'value',}}},['a', 'b', 'c'])
    ['value']
    >>> get_list({'a':{'b': {'c': ['value1', 'value2']}}},['a', 'b', 'c'])
    ['value1', 'value2']
    """
    if isinstance(keys, str):
        keys = [keys]
    try:
        result = functools.reduce(lambda dict_obj, key: dict_obj[key], keys, dict_item)
    except (KeyError, TypeError):
        result = []

    if not isinstance(result, list):
        result = [result]

    return result
