import dataclasses as dcs


@dcs.dataclass
class BaseWidget:
    width: int
    height: int
    anchor: tuple[int, int]
    content: list[str]
    line_range: tuple[int, int | float]
    col_range: tuple[int, int | float]


class MainBox(BaseWidget):
    pass
