from enum import StrEnum
from typing import Literal, IO

class TrackType(StrEnum):
    INFO = "\033[32m"
    DEFAULT = "\033[0m"
    ERROR = "\033[31m"

def traceBack(*values: object,
                delimiter: str | None = '\t',
                sep: str | None = " ",
                end: str | None = "\n",
                file: IO[str] | None = None,
                flush: Literal[False] = False,
                type: TrackType | None = TrackType.INFO) -> None:
    prefix: str = f"{type}{type.name}{TrackType.DEFAULT}:"
    message: str = sep.join(map(str, values))

    print(prefix + delimiter + message, end=end, file=file, flush=flush)