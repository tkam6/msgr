import dataclasses as dcs
import typing as ty

if ty.TYPE_CHECKING:
    from src import renderer as ren

type Dimen = int | ty.Callable[["ren.Win"], int]
type Anchor = tuple[Dimen, Dimen]
type Range = tuple[Dimen, Dimen | float]


@dcs.dataclass
class BaseWidget:
    width: Dimen
    height: Dimen
    anchor: Anchor
    content: list[str]
    line_range: Range
    col_range: Range
    alignment: int = -1
    border: bool = False


class MainBox(BaseWidget):
    pass


class ConvoList(BaseWidget):
    pass


class ConvoEntry(BaseWidget):
    pass
