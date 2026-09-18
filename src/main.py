#!/usr/bin/env -S python3 -BOO
import curses as cur
import math
import time

from src import general as gen
from src import renderer as ren
from src import widgets as wgts


def main(scr: cur.window) -> list[int]:
    win = ren.Win(scr)
    widget_list = {
        "convo-list": wgts.ConvoList(
            height=win.term_sz[0] - 20,
            width=win.term_sz[1] - 20,
            anchor=(-10, -10),
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

    total = 0
    frames = 0
    last = time.perf_counter_ns()
    while True:
        key = win.getch()
        if gen.is_key(key, ("q", "Q")):
            break
        win.erase()
        win.draw(widget_list)
        win.refresh()
        now = time.perf_counter_ns()
        total += now - last
        frames += 1
        last = now

    return (total, frames)


if __name__ == "__main__":
    try:
        total, frames = cur.wrapper(main)
        print("TOTAL FRAMES", frames)
        print(f"TOTAL FRAME TIME {round(total * 1e-9, 3)}s")
        print("AVG FRAME RATE", round(frames / (total * 1e-9)))
    except (KeyboardInterrupt, EOFError):
        pass
