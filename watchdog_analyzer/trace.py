import collections
import json
import typing

from watchdog_analyzer.dump import Dump

_KeyType = typing.TypeVar('_KeyType')  # Key type.
_CovariantType = typing.TypeVar('_CovariantType', covariant=True)  # Any type covariant containers.
_CovariantValueType = typing.TypeVar('_CovariantValueType', covariant=True)  # Value type covariant containers.


class Trace(typing.Mapping, collections.Mapping):
    def __init__(self, dump: Dump, no_cache: bool = True):
        self._dump = dump
        self._path = dump.path.with_suffix('.trace')
        self._trace: dict
        self._should_save: bool

        if no_cache is False and self._path.exists() and self._path.is_file():
            print(f"Detected trace: '{self._path}'")
            with self._path.open('r') as f:
                self._trace = json.load(f)
            self._should_save = False
        else:
            print(f"Building trace: '{self._path}' ...")
            self._trace = dict()
            with self._dump.path.open('r') as f:
                for record in map(json.loads, f.readlines()):
                    record['link'] = f"{record['file']}:{record['line']}"
                    data = self._trace.setdefault(record['PID'], {})
                    if isinstance(record['address'], dict):
                        address = record['address']
                        data.setdefault(address['to'], data.pop(address['from'], [])).insert(0, record)
                    else:
                        data.setdefault(record['address'], []).insert(0, record)
            self._should_save = True

    def save(self) -> None:
        if self._should_save:
            print(f"Saving trace: '{self._path}' ...")
            with self._path.open('w') as f:
                json.dump(self._trace, f)

    def __getitem__(self, k: _KeyType) -> _CovariantValueType:
        return self._trace.__getitem__(k)

    def __len__(self) -> int:
        return self._trace.__len__()

    def __iter__(self) -> typing.Iterator[_CovariantType]:
        return self._trace.__iter__()
