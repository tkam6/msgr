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
        cur.curs_set(0)
        self.scr.nodelay(True)
        self.scr.keypad(True)

        self.term_sz = self.scr.getmaxyx()
        self.clear = self.scr.clear
        self.erase = self.scr.erase
        self.refresh = self.scr.refresh

    def addch(self, y: int, x: int, c: str) -> None:
        try:
            self.scr.addch(y, x, c)
        except cur.error:
            if not (y == self.term_sz[0] - 1 and x == self.term_sz[1] - 1):
                raise

    def addnstr(self, y: int, x: int, s: str, n: int, attr: int | None = None) -> None:
        try:
            if attr is None:
                self.scr.addnstr(y, x, s, n)
            else:
                self.scr.addnstr(y, x, s, n, attr)
        except cur.error:
            if not (y == self.term_sz[0] - 1 and x + n < self.term_sz[1]):
                raise

    def chk_cell_visibility(self, y: int, x: int) -> bool:
        return 0 <= y < self.term_sz[0] and 0 <= x < self.term_sz[1]

    def get_bitwise_or(self, arr: ty.Iterable[int]) -> int | None:
        if not arr:
            return None
        res = arr[0]
        for i in arr[1 :]:
            res = res | i
        return res

    # TODO: make dimensions and anchors include lambdas and functions for
    # dynamic dimensions
    def draw(self, widget_list: "dict[str, wgts.BaseWidget]") -> None:
        self.term_sz = self.scr.getmaxyx()

        for name, widget in widget_list.items():
            width = widget.width(self, widget) if callable(widget.width) else widget.width
            height = widget.height(self, widget) if callable(widget.height) else widget.height
            anchor = (
                widget.anchor[0](self, widget) if callable(widget.anchor[0]) else widget.anchor[0],
                widget.anchor[1](self, widget) if callable(widget.anchor[1]) else widget.anchor[1],
            )
            line_range = (
                widget.line_range[0](self, widget) if callable(widget.line_range[0]) else widget.line_range[0],
                widget.line_range[1](self, widget) if callable(widget.line_range[1]) else widget.line_range[1],
            )
            col_range = (
                widget.col_range[0](self, widget) if callable(widget.col_range[0]) else widget.col_range[0],
                widget.col_range[1](self, widget) if callable(widget.col_range[1]) else widget.col_range[1],
            )
            actual_width = width - (2 if widget.border else 0)
            actual_height = height - (2 if widget.border else 0)
            y = anchor[0] + (1 if widget.border else 0)
            x = anchor[1] + (1 if widget.border else 0)
            line_range1 = line_range[1]
            col_range1 = col_range[1]

            # line and column ranges first indices aren't supposed to be inf
            if math.isinf(line_range[0]):
                raise RuntimeError(f"Widget '{name}': Line range first element cannot be inf")
            if math.isinf(col_range[0]):
                raise RuntimeError(f"Widget '{name}': Column range first element cannot be inf")
            # if line or column ranges second indices are inf, change them to
            # length of corresponding whatever
            if math.isinf(line_range1):
                line_range1 = len(widget.content)
            if math.isinf(col_range1):
                col_range1 = (
                    len(max([line for line, *attrs in widget.content], key=len))
                    if widget.content else 0
                )
            # extract lines and columns that are in range
            lines = widget.content[line_range[0] : line_range1]
            to_draw = [
                (line[col_range[0] : col_range1], attrs)
                for line, *attrs in lines
            ]

            # draw only top-left-most part of extracted range lines and columns
            for idx, (line, attrs) in enumerate(to_draw[: actual_height]):
                if y + idx > self.term_sz[0] - 1:
                    break
                self.addnstr(
                    y + idx,
                    x,
                    line[: actual_width],
                    self.term_sz[1] - x - 1,
                    attr=self.get_bitwise_or(attrs)
                )

            # draw widget borders
            if widget.border:
                if height < 2:
                    raise RuntimeError(f"Widget '{name}': Cannot draw every damn thing in the space you've given")

                # LEFT AND RIGHT (VERTICAL) BORDERS, CHAR-BY-CHAR
                # TODO: implement clipping for vertical border lines
                for i in range(actual_height):
                    left_cell = (y + i, anchor[1])
                    right_cell = (y + i, anchor[1] + width - 1)
                    if self.chk_cell_visibility(*left_cell):
                        self.addch(*left_cell, gen.ROUND_CHS["vertical"])
                    if self.chk_cell_visibility(*right_cell):
                        self.addch(*right_cell, gen.ROUND_CHS["vertical"])

                # For some blizzare reason, I couldn't accomodate these inside
                # a single addnstr call. It left out the top-right and
                # bottom-right corner for some reason. But I prefer it this
                # way, as separate calls for corners and edges

                # TOP AND BOTTOM BORDER, CHAR-BY-CHAR
                topleft_cell = (anchor[0], anchor[1])
                topright_cell = (anchor[0], anchor[1] + width - 1)
                btmleft_cell = (anchor[0] + height - 1, anchor[1])
                btmright_cell = (anchor[0] + height - 1, anchor[1] + width - 1)
                # top-left cell
                if self.chk_cell_visibility(*topleft_cell):
                    self.addch(*topleft_cell, gen.ROUND_CHS["top-left"])

                # horizontal line, char-by-char
                # TODO: implement clipping for horizontal border lines
                for i in range(actual_width):
                    top_cell = (anchor[0], x + i)
                    btm_cell = (anchor[0] + height - 1, x + i)
                    # top horizontal
                    if self.chk_cell_visibility(*top_cell):
                        self.addch(*top_cell, gen.ROUND_CHS["horizontal"])
                    # bottom horizontal
                    if self.chk_cell_visibility(*btm_cell):
                        self.addch(*btm_cell, gen.ROUND_CHS["horizontal"])

                # top-right cell
                if self.chk_cell_visibility(*topright_cell):
                    self.addch(*topright_cell, gen.ROUND_CHS["top-right"])
                if self.chk_cell_visibility(*btmleft_cell):
                    self.addch(*btmleft_cell, gen.ROUND_CHS["bottom-left"])
                if self.chk_cell_visibility(*btmright_cell):
                    self.addch(*btmright_cell, gen.ROUND_CHS["bottom-right"])
