from pathlib import Path
import typing

from watchdog_analyzer.panic import panic


class Dump:
    def __init__(self, path: typing.Union[Path, str]):
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            panic(f"Path: '{path}' does not exist")
        if not path.is_file():
            panic(f"Path: '{path}' is not a file")
        if not self.match_format(path):
            panic(f"Path: '{path}' unrecognized format")
        self._path = path

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
        timestamps = sorted(
            map(lambda f: int(f.with_suffix('').name.split("-")[1]),
                filter(cls.match_format, path.iterdir())))

        if not timestamps:
            panic(f"No dump files found")

        self = cls(path.joinpath(f"watchdog-{timestamps[-1]}").with_suffix(".jsonl"))
        print(f"Detected dump: '{self}'")
        return self

    @classmethod
    def match_format(cls, path: Path) -> bool:
        return path.name.startswith("watchdog-") and path.suffix == ".jsonl"

    def __repr__(self):
        return str(self._path)
