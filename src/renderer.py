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
            range0 = widget.range_[0]
            range1 = widget.range_[1]
            if math.isinf(range0):
                raise RuntimeError(f"Widget {name}: Range first element cannot be inf")
            if math.isinf(range1):
                range1 = len(widget.content)
            lines = widget.content[range0 : range1]
            if not lines:
                raise RuntimeError(f"Widget {name}: Invalid range [{range0}, {range1}); nothing to display")

            for idx, line in enumerate(lines):
                self.scr.addnstr(widget.anchor[0] + idx, widget.anchor[1], line, self.term_sz[0])
