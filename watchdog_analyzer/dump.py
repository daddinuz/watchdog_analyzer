from pathlib import Path
import re
import typing

from watchdog_analyzer.panic import panic


class Dump:
    _FORMAT = re.compile('\.watchdog-([0-9]+)-([0-9]+)\.jsonl')

    class _VersionAndTimestamp(typing.NamedTuple):
        version: int
        timestamp: int

    def __init__(self, path: typing.Union[Path, str]):
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            panic(f"Path: '{path}' does not exist")
        if not path.is_file():
            panic(f"Path: '{path}' is not a file")
        self._path = path
        self._version, self._timestamp = self._extract_version_and_timestamp(path)

    @property
    def path(self) -> Path:
        return self._path

    @classmethod
    def scan_directory(cls, path: typing.Union[Path, str]) -> 'Dump':
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            panic(f"Path: '{path}' does not exist")
        if not path.is_dir():
            panic(f"Path: '{path}' is not a directory")

        print(f"Scanning directory: '{path}' ...")
        versions_and_timestamps: typing.List[cls._VersionAndTimestamp] = \
            sorted(map(cls._extract_version_and_timestamp,
                       filter(cls._match_format, path.iterdir())),
                   key=lambda o: o.timestamp)

        if not versions_and_timestamps:
            panic(f"No dump files found")

        self = cls(path.joinpath(f".watchdog-{'-'.join(map(str, versions_and_timestamps[-1]))}").with_suffix(".jsonl"))
        print(f"Detected dump: '{self}'")
        return self

    @classmethod
    def _match_format(cls, path: Path) -> bool:
        return bool(cls._FORMAT.fullmatch(path.name))

    # noinspection PyProtectedMember
    @classmethod
    def _extract_version_and_timestamp(cls, path: Path) -> 'Dump._VersionAndTimestamp':
        match = cls._FORMAT.fullmatch(path.name)
        if not match:
            panic(f"Path: '{path}' unrecognized format")
        return cls._VersionAndTimestamp(*map(int, match.groups()))

    def __repr__(self):
        return str(self._path)
