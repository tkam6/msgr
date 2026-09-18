import curses as cur
import math
import typing as ty

from src import general as gen

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
        self.clear = self.scr.clear

    def addch(self, y: int, x: int, c: str) -> None:
        try:
            self.scr.addch(y, x, c)
        except cur.error:
            if not (y == self.term_sz[0] - 1 and x == self.term_sz[1] - 1):
                raise

    def addnstr(self, y: int, x: int, s: str, n: int) -> None:
        try:
            self.scr.addnstr(y, x, s, n)
        except cur.error:
            if not (y == self.term_sz[0] - 1 and x + n < self.term_sz[1]):
                raise

    def draw(self, widget_list: "dict[str, wgts.BaseWidget]") -> None:
        self.term_sz = self.scr.getmaxyx()

        for name, widget in widget_list.items():
            actual_width = widget.width - (2 if widget.border else 0)
            actual_height = widget.height - (2 if widget.border else 0)
            y = widget.anchor[0] + (1 if widget.border else 0)
            x = widget.anchor[1] + (1 if widget.border else 0)
            line_range0 = widget.line_range[0]
            line_range1 = widget.line_range[1]
            col_range0 = widget.col_range[0]
            col_range1 = widget.col_range[1]
            # line and column ranges first indices aren't supposed to be inf
            if math.isinf(line_range0):
                raise RuntimeError(f"Widget '{name}': Line range first element cannot be inf")
            if math.isinf(col_range0):
                raise RuntimeError(f"Widget '{name}': Column range first element cannot be inf")
            # if line or column ranges second indices are inf, change them to
            # length of corresponding whatever
            if math.isinf(line_range1):
                line_range1 = len(widget.content)
            if math.isinf(col_range1):
                col_range1 = (
                    len(max([line for line in widget.content], key=len))
                    if widget.content else 0
                )
            # gen.debug_file.write(f"{line_range1}, {col_range1}\n")
            # extract lines and columns that are in range
            # TODO: remove these checks if needed; only for debugging and testing
            lines = widget.content[line_range0 : line_range1]
            if not lines:
                raise RuntimeError(f"Widget '{name}': Invalid line range [{line_range0}, {line_range1}); nothing to display")
            to_draw = [line[col_range0 : col_range1] for line in lines]
            if not to_draw:
                raise RuntimeError(f"Widget '{name}': Invalid column range [{col_range0}, {col_range1}); nothing to display")

            # draw only top-left-most part of extracted range lines and columns
            for idx, line in enumerate(to_draw[: actual_height]):
                if y + idx > self.term_sz[0] - 1:
                    break
                self.addnstr(y + idx, x, line[: actual_width], self.term_sz[1] - x - 1)

            # draw widget borders
            if widget.border:
                # left and right borders
                for i in range(widget.anchor[0] + 1, widget.anchor[0] + widget.height - 1):
                    self.addch(
                        widget.anchor[0] + i,
                        widget.anchor[1],
                        gen.ROUND_CHS["vertical"],
                    )
                    self.addch(
                        widget.anchor[0] + i,
                        widget.anchor[1] + widget.width - 1,
                        gen.ROUND_CHS["vertical"],
                    )

                # for some blizzare reason, i couldn't accomodate these inside
                # a single addnstr call. it left out the top-right and
                # bottom-right corner for some reason. but i prefer it this
                # way, as separate calls for corners and edges

                # top border
                self.addch(widget.anchor[1], widget.anchor[0], gen.ROUND_CHS["top-left"])
                self.addnstr(
                    widget.anchor[1],
                    widget.anchor[0] + 1,
                    gen.ROUND_CHS["horizontal"] * actual_width,
                    self.term_sz[1] - widget.anchor[1] - 1,
                )
                self.addch(widget.anchor[1], widget.anchor[0] + widget.width - 1, gen.ROUND_CHS["top-right"])
                # bottom border
                self.addch(widget.anchor[1] + widget.height - 1, widget.anchor[0], gen.ROUND_CHS["bottom-left"])
                self.addnstr(
                    widget.anchor[1] + widget.height - 1,
                    widget.anchor[0] + 1,
                    gen.ROUND_CHS["horizontal"] * actual_width,
                    self.term_sz[1] - widget.anchor[1] - 1,
                )
                self.addch(widget.anchor[1] + widget.height - 1, widget.anchor[0] + widget.width - 1, gen.ROUND_CHS["bottom-right"])
