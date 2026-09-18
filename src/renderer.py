import atexit
import curses as cur
import math
import typing as ty

if ty.TYPE_CHECKING:
    from src import widgets as wgts


class Win:
    def __init__(self, scr: cur.window) -> None:
        self.scr = scr
        cur.noecho()
        cur.cbreak()
        self.scr.nodelay(True)
        self.scr.keypad(True)

        self.term_sz = self.scr.getmaxyx()

        self.getch = self.scr.getch
        self.getkey = self.scr.getkey
        self.refresh = self.scr.refresh

    def draw(self, widget_list: "dict[str, wgts.BaseWidget]") -> None:
        self.term_sz = self.scr.getmaxyx()

        for name, widget in widget_list.items():
            y = widget.anchor[0]
            x = widget.anchor[1]
            line_range0 = widget.line_range[0]
            line_range1 = widget.line_range[1]
            col_range0 = widget.col_range[0]
            col_range1 = widget.col_range[1]
            # line and column ranges first indices aren't supposed to be inf
            if math.isinf(line_range0):
                raise RuntimeError(f"Widget {name}: Line range first element cannot be inf")
            if math.isinf(col_range0):
                raise RuntimeError(f"Widget {name}: Column range first element cannot be inf")
            # if line or column ranges second indices are inf, change them to
            # length of corresponding whatever
            if math.isinf(line_range1):
                line_range1 = len(widget.content)
            if math.isinf(col_range1):
                col_range1 = (
                    len(max([line for line in widget.content], key=len))
                    if widget.content else 0
                )
            # extract lines and columns that are in range
            lines = widget.content[line_range0 : line_range1]
            if not lines:
                raise RuntimeError(f"Widget {name}: Invalid range [{line_range0}, {line_range1}); nothing to display")
            to_draw = [line[col_range0 : col_range1] for line in lines]

            # draw only top-left-most part of extracted range lines and columns
            for idx, line in enumerate(to_draw[: widget.height]):
                if y + idx > self.term_sz[0] - 1:
                    break
                self.scr.addnstr(y + idx, x, line[: widget.width], self.term_sz[1] - widget.width)
