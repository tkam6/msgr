import dataclasses as dcs


@dcs.dataclass
class BaseWidget:
    width: int
    height: int
    anchor: tuple[int, int]
    content: list[str]
    range_: tuple[int, int | float]
    chop: bool = True
