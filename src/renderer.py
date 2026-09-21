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

        self.screen_buf = np.empty((0, 0), dtype="U1")
        self.attr_buf = np.empty((0, 0), dtype=np.int32)

    def addch(self, y: int, x: int, c: str, attr: int) -> None:
        try:
            self.scr.addch(y, x, c, attr)
        except cur.error:
            if y != self.term_sz[0] - 1 or x != self.term_sz[1] - 1:
                raise

    def addnstr(self, y: int, x: int, s: str, n: int, attr: int) -> None:
        try:
            self.scr.addnstr(y, x, s, n, attr)
        except cur.error:
            if y != self.term_sz[0] - 1:
                raise

    def chk_cell_visibility(self, y: int, x: int) -> bool:
        return 0 <= y < self.term_sz[0] and 0 <= x < self.term_sz[1]

    def get_bitwise_or(self, arr: ty.Iterable[int]) -> int | None:
        if not arr:
            return 0
        res = arr[0]
        for i in arr[1 :]:
            res = res | i
        return res

    def draw(self, widget_list: "dict[str, wgts.BaseWidget]") -> None:
        self.term_sz = self.scr.getmaxyx()
        if self.screen_buf.shape != self.term_sz or self.attr_buf.shape != self.term_sz:
            self.screen_buf = np.empty(self.term_sz, dtype="U1")
            self.attr_buf = np.empty(self.term_sz, dtype=np.int32)
        self.screen_buf.fill("\x00")
        self.attr_buf.fill(0)

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
            attr_new_buf = np.zeros((height, width), dtype=np.int32)

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

            border_len_y = abs(y - anchor[0])
            # draw only top-left-most part of extracted range lines and columns
            for idx, (line, attrs) in enumerate(to_draw[: actual_height], start=border_len_y):
                if y + idx > self.term_sz[0] - 1:
                    break
                line_trimmed = line[: actual_width]

                right_shift = 0
                # centre alignment
                if widget.alignment == 0:
                    right_shift = (actual_width - len(line_trimmed)) // 2
                # right alignment
                elif widget.alignment == 1:
                    right_shift = actual_width - len(line_trimmed)

                border_len_x = abs(x - anchor[1])
                new_buf[idx, border_len_x + right_shift : border_len_x + right_shift + len(line_trimmed)] = list(line_trimmed)
                attr_new_buf[idx, border_len_x + right_shift : border_len_x + right_shift + len(line_trimmed)] = self.get_bitwise_or(attrs)

            # DRAW WIDGET BORDERS
            if widget.border:
                if height < 2:
                    raise RuntimeError(f"Widget '{name}': Cannot draw every damn thing in the space you've given")
                if widget.border_type is None:
                    raise RuntimeError(f"Widget '{name}': Borders enabled, but no border type specified")
                borders = gen.BORDERS[widget.border_type]

                # vertical border lines
                new_buf[1 : height - 1, 0] = borders["vertical"]
                new_buf[1 : height - 1, width - 1] = borders["vertical"]

                topleft_cell = (0, 0)
                topright_cell = (0, width - 1)
                btmleft_cell = (height - 1, 0)
                btmright_cell = (height - 1, width - 1)
                new_buf[topleft_cell[0]][topleft_cell[1]] = borders["top-left"]
                new_buf[topright_cell[0]][topright_cell[1]] = borders["top-right"]
                new_buf[btmleft_cell[0]][btmleft_cell[1]] = borders["bottom-left"]
                new_buf[btmright_cell[0]][btmright_cell[1]] = borders["bottom-right"]

                # horizontal border lines
                new_buf[0, 1 : width - 1] = borders["horizontal"]
                new_buf[height - 1, 1 : width - 1] = borders["horizontal"]

            widget_y_start = max(0, -anchor[0])
            widget_x_start = max(0, -anchor[1])
            screen_y_start = max(0, anchor[0])
            screen_x_start = max(0, anchor[1])

            visible_y_len = min(height - widget_y_start, self.term_sz[0] - screen_y_start)
            visible_x_len = min(width - widget_x_start, self.term_sz[1] - screen_x_start)

            widget_y_end = widget_y_start + visible_y_len
            widget_x_end = widget_x_start + visible_x_len
            screen_y_end = screen_y_start + visible_y_len
            screen_x_end = screen_x_start + visible_x_len

            widget_part = new_buf[widget_y_start : widget_y_end, widget_x_start : widget_x_end]
            screen_part = self.screen_buf[screen_y_start : screen_y_end, screen_x_start : screen_x_end]
            mask = widget_part != "\x00"
            screen_part[:] = np.where(mask, widget_part, screen_part)

            # for attributes
            attr_widget_part = attr_new_buf[widget_y_start : widget_y_end, widget_x_start : widget_x_end]
            attr_screen_part = self.attr_buf[screen_y_start : screen_y_end, screen_x_start : screen_x_end]
            attr_mask = attr_widget_part != 0
            attr_screen_part[:] = np.where(attr_mask, attr_widget_part, attr_screen_part)


        for i in range(self.screen_buf.shape[0]):
            row = self.screen_buf[i]
            attr_row = self.attr_buf[i]
            row[row == "\x00"] = " "

            change_idxs = np.flatnonzero(np.diff(attr_row)) + 1
            starts = np.concatenate(([0], change_idxs))
            ends = np.concatenate((change_idxs, [len(attr_row)]))

            for start, end in zip(starts, ends):
                run_len = end - start
                s = row[start : end].view(f"U{run_len}")[0]
                self.addnstr(i, start, s, run_len, int(attr_row[start]))
