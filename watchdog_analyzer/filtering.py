import typing

from watchdog_analyzer.chainable_iterator import ChainableIterator

Key, Value = typing.Any, typing.Any
KeyPath = typing.List[Key]
Predicate = typing.Callable[[KeyPath, Key, Value], bool]
_Node = typing.NamedTuple('Node', (('key_path', KeyPath), ('data', typing.Mapping)))


def _match_all(_p: KeyPath, _k: Key, _v: Value) \
        -> bool:
    return True


def _decompose_dict(the_dict: typing.Mapping, predicate: Predicate = _match_all) \
        -> typing.Generator[typing.Tuple[KeyPath, Value], None, None]:
    root = ChainableIterator((_Node([], the_dict),))
    for node in root:
        key_path = node.key_path
        for k, v in node.data.items():
            key_path.append(k)
            if isinstance(v, dict):
                root.chain((_Node(key_path, v),))
            if predicate(key_path, k, v):
                yield key_path, v
            key_path = key_path[:-1]


def _recompose_dict(items: typing.Iterator[typing.Tuple[KeyPath, Value]]) \
        -> typing.Mapping:
    root = {}
    for path, value in items:
        base, last = root, len(path) - 1
        for i, key in enumerate(path):
            base = base.setdefault(key, {} if i < last else value)
    return root


def filter_dict(the_dict: typing.Mapping, predicate: Predicate = _match_all) \
        -> typing.Mapping:
    return _recompose_dict(_decompose_dict(the_dict, predicate))
