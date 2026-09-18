#!/usr/bin/env -S python3 -BOO
import curses as cur
import math

from src import general as gen
from src import renderer as ren
from src import widgets as wgts


def main(scr: cur.window) -> None:
    win = ren.Win(scr)
    widget_list = {
        "convo-list": wgts.ConvoList(
            height=win.term_sz[0] - 20,
            width=win.term_sz[1] - 20,
            anchor=(100, 5),
            content=[],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=-1,
            border=True,
        ),
        "test": wgts.MainBox(
            height=win.term_sz[0],
            width=win.term_sz[1],
            anchor=(0, 0),
            content=[],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=-1,
            border=True,
        ),
    }

    while True:
        key = win.getch()
        if gen.is_key(key, ("q", "Q")):
            break
        win.draw(widget_list)
        win.refresh()


if __name__ == "__main__":
    try:
        cur.wrapper(main)
    except (KeyboardInterrupt, EOFError):
        pass
