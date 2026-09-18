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

    def chk_point_visibility(self, y: int, x: int) -> bool:
        return 0 <= y < self.term_sz[0] and 0 <= x < self.term_sz[1]

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
            # extract lines and columns that are in range
            lines = widget.content[line_range0 : line_range1]
            to_draw = [line[col_range0 : col_range1] for line in lines]

            # draw only top-left-most part of extracted range lines and columns
            for idx, line in enumerate(to_draw[: actual_height]):
                if y + idx > self.term_sz[0] - 1:
                    break
                self.addnstr(y + idx, x, line[: actual_width], self.term_sz[1] - x - 1)

            # draw widget borders
            if widget.border:
                # left and right (vertical) borders, char-by-char
                for i in range(actual_height):
                    left_cell = (y + i, widget.anchor[1])
                    right_cell = (y + i, widget.anchor[1] + widget.width - 1)
                    if self.chk_point_visibility(*left_cell):
                        self.addch(*left_cell, gen.ROUND_CHS["vertical"])
                    if self.chk_point_visibility(*right_cell):
                        self.addch(*right_cell, gen.ROUND_CHS["vertical"])

                # For some blizzare reason, I couldn't accomodate these inside
                # a single addnstr call. It left out the top-right and
                # bottom-right corner for some reason. But I prefer it this
                # way, as separate calls for corners and edges

                # TOP AND BOTTOM BORDER, CHAR-BY-CHAR
                topleft_cell = (widget.anchor[0], widget.anchor[1])
                topright_cell = (widget.anchor[0], widget.anchor[1] + widget.width - 1)
                btmleft_cell = (widget.anchor[0] + widget.height - 1, widget.anchor[1])
                btmright_cell = (widget.anchor[0] + widget.height - 1, widget.anchor[1] + widget.width - 1)
                # top-left cell
                if self.chk_point_visibility(*topleft_cell):
                    self.addch(*topleft_cell, gen.ROUND_CHS["top-left"])
                # horizontal line, char-by-char
                for i in range(actual_width):
                    top_cell = (widget.anchor[0], x + i)
                    btm_cell = (widget.anchor[0] + widget.height - 1, x + i)
                    # top horizontal
                    if self.chk_point_visibility(*top_cell):
                        self.addch(*top_cell, gen.ROUND_CHS["horizontal"])
                    # bottom horizontal
                    if self.chk_point_visibility(*btm_cell):
                        self.addch(*btm_cell, gen.ROUND_CHS["horizontal"])
                # top-right cell
                if self.chk_point_visibility(*topright_cell):
                    self.addch(*topright_cell, gen.ROUND_CHS["top-right"])
                if self.chk_point_visibility(*btmleft_cell):
                    self.addch(*btmleft_cell, gen.ROUND_CHS["bottom-left"])
                if self.chk_point_visibility(*btmright_cell):
                    self.addch(*btmright_cell, gen.ROUND_CHS["bottom-right"])
