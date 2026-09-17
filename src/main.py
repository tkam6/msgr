#!/usr/bin/env -S python3 -BOO
import curses as cur
import math

from src import general as gen
from src import renderer as ren
from src import widgets as wgts


def main(scr: cur.window) -> None:
    win = ren.Win(scr)
    widget_list = {
        "test": wgts.BaseWidget(
            width=10,
            height=5,
            anchor=(2, 2),
            content=["Hello world"],
            range_=[0, math.inf],
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
