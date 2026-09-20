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
    border_type: str | None = None


class MainBox(BaseWidget):
    pass


class ConvoList(BaseWidget):
    pass


class ConvoEntry(BaseWidget):
    pass


class Label(BaseWidget):
    pass


def anchor_vert_centre(win: "ren.Win", widget: BaseWidget) -> int:
    if callable(widget.height):
        return (win.term_sz[0] - widget.height(win, widget)) // 2
    return (win.term_sz[0] - widget.height) // 2


def anchor_hori_centre(win: "ren.Win", widget: BaseWidget) -> int:
    if callable(widget.width):
        return (win.term_sz[1] - widget.width(win, widget)) // 2
    return (win.term_sz[1] - widget.width) // 2


anchor_centre = (anchor_vert_centre, anchor_hori_centre)
