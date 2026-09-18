import dataclasses as dcs
import typing as ty

from src import general as gen

if ty.TYPE_CHECKING:
    from src import renderer as ren

type Dimen = int | ty.Callable[["ren.Win"], int]
type Anchor = tuple[Dimen, Dimen]
type Range = tuple[Dimen, Dimen | float]

anchor_centre = (
    lambda win, widget: (win.term_sz[0] - widget.height(win, widget) if callable(widget.height) else widget.height) // 2,
    lambda win, widget: (win.term_sz[1] - widget.width(win, widget) if callable(widget.width) else widget.height) // 2,
)


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
