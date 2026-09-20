import curses as cur
import math
import sys
import typing as ty

import numpy as np

from src import general as gen

if ty.TYPE_CHECKING:
    from src import widgets as wgts

np.set_printoptions(threshold=sys.maxsize)


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
            if y != self.term_sz[0] - 1:
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

    def draw(self, widget_list: "dict[str, wgts.BaseWidget]") -> None:
        self.term_sz = self.scr.getmaxyx()
        screen_buf = np.full(self.term_sz, "\x00", dtype="U1")

        for widget in widget_list:
            name = widget.name
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
            new_buf = np.full((height, width), "\x00", dtype="U1")

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

                right_shift = 0
                # centre alignment
                if widget.alignment == 0:
                    right_shift = (actual_width - len(line[: actual_width])) // 2
                # right alignment
                elif widget.alignment == 1:
                    right_shift = actual_width - len(line[: actual_width])

                new_buf[idx][right_shift : actual_width - right_shift] = line[: actual_width - right_shift]

            # DRAW WIDGET BORDERS
            if not widget.border:
                continue

            if height < 2:
                raise RuntimeError(f"Widget '{name}': Cannot draw every damn thing in the space you've given")
            if widget.border_type is None:
                raise RuntimeError(f"Widget '{name}': Borders enabled, but no border type specified")
            borders = gen.BORDERS[widget.border_type]

            # LEFT AND RIGHT (VERTICAL) BORDERS, CHAR-BY-CHAR
            # TODO: implement clipping for vertical border lines
            # vertical lines, char-by-char
            for i in range(1, actual_height + 1):
                left_cell = (i, 0)
                right_cell = (i, width - 1)
                # left vertical
                new_buf[left_cell[0]][left_cell[1]] = borders["vertical"]
                # right vertical
                new_buf[right_cell[0]][right_cell[1]] = borders["vertical"]

            # TOP AND BOTTOM BORDER, CHAR-BY-CHAR
            topleft_cell = (0, 0)
            topright_cell = (0, width - 1)
            btmleft_cell = (height - 1, 0)
            btmright_cell = (height - 1, width - 1)
            # top-left cell
            new_buf[topleft_cell[0]][topleft_cell[1]] = borders["top-left"]
            new_buf[topright_cell[0]][topright_cell[1]] = borders["top-right"]
            new_buf[btmleft_cell[0]][btmleft_cell[1]] = borders["bottom-left"]
            new_buf[btmright_cell[0]][btmright_cell[1]] = borders["bottom-right"]

            # TODO: implement clipping for horizontal border lines
            # horizontal line, char-by-char
            for i in range(1, actual_width + 1):
                top_cell = (0, i)
                btm_cell = (height - 1, i)
                # top horizontal
                new_buf[top_cell[0]][top_cell[1]] = borders["horizontal"]
                # bottom horizontal
                new_buf[btm_cell[0]][btm_cell[1]] = borders["horizontal"]

            widget_y_start = max(0, -anchor[0])
            widget_x_start = max(0, -anchor[1])
            screen_y_start = max(0, anchor[0])
            screen_x_start = max(0, anchor[1])

            visible_y_len = min(height + widget_y_start, self.term_sz[0] - screen_y_start)
            visible_x_len = min(height + widget_x_start, self.term_sz[1] - screen_x_start)

            widget_y_end = widget_y_start + visible_y_len
            widget_x_end = widget_x_start + visible_x_len
            screen_y_end = screen_y_start + visible_y_len
            screen_x_end = screen_x_start + visible_x_len

            widget_part = new_buf[widget_y_start : widget_y_end, widget_x_start : widget_x_end]
            screen_part = screen_buf[screen_y_start : screen_y_end, screen_x_start : screen_x_end]
            mask = widget_part != "\x00"

            screen_part[:] = np.where(mask, widget_part, screen_part)

        with open("all.log", "w") as f:
            for i, row in enumerate(screen_buf):
                print(self.term_sz[1], file=f)
                row[row == "\x00"] = " "
            self.addnstr(i, 0, "".join(row), self.term_sz[1])
