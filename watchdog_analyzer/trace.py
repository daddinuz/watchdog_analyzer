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
            relocated_records = list()
            with self._dump.path.open('r') as f:
                for record in map(json.loads, f.readlines()):
                    pid = self._key_by_pid(record['PID'])
                    file = self._key_by_file(record['file'])
                    func = self._key_by_func(record['func'])

                    data = self._trace.setdefault(pid, {}).setdefault(file, {}).setdefault(func, {})
                    if isinstance(record['address'], dict):
                        relocated_records.append(record)
                    else:
                        data.setdefault(self._key_by_address(record['address']), []).append(record)

                for record in relocated_records:
                    assert isinstance(record['address'], dict)
                    pid = self._key_by_pid(record['PID'])
                    file = self._key_by_file(record['file'])
                    func = self._key_by_func(record['func'])
                    from_address = self._key_by_address(record['address']['from'])
                    to_address = self._key_by_address(record['address']['to'])

                    data = self._trace[pid][file][func]
                    data.setdefault(to_address, data.pop(from_address, [])).append(record)
                    data[to_address].sort(key=lambda d: d['line'])
            self._should_save = True

    def save(self) -> None:
        if self._should_save:
            print(f"Saving trace: '{self._path}' ...")
            with self._path.open('w') as f:
                json.dump(self._trace, f)

    @classmethod
    def _key_by_pid(cls, pid: str) -> str:
        return f"PID: {pid}"

    @classmethod
    def _key_by_file(cls, file: str) -> str:
        return f"file: {file}"

    @classmethod
    def _key_by_func(cls, func: str) -> str:
        return f"func: {func}"

    @classmethod
    def _key_by_address(cls, address: str) -> str:
        return f"address: {address}"

    def __getitem__(self, k: _KeyType) -> _CovariantValueType:
        return self._trace.__getitem__(k)

    def __len__(self) -> int:
        return self._trace.__len__()

    def __iter__(self) -> typing.Iterator[_CovariantType]:
        return self._trace.__iter__()
