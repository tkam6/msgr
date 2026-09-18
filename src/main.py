#!/usr/bin/env -S python3 -BOO
import curses as cur
import dataclasses as dcs
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
        "test2": wgts.BaseWidget(
            height=10,
            width=20,
            anchor=(10, 30),
            content=["hello world"],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=-1,
            border=True,
        )
    }

    frame_time = 1 / gen.FPS
    total = 0
    frames = 0
    last = time.perf_counter()
    while True:
        key = win.scr.getch()
        if gen.is_key(key, ("q", "Q")):
            break
        elif key == cur.KEY_RESIZE:
            win.term_sz = win.scr.getmaxyx()
            cur.resize_term(*win.term_sz)
        win.erase()
        win.draw(widget_list)
        win.refresh()

        # frame rate limiter
        time.sleep(max(0, frame_time - (time.perf_counter() - last)))
        # for frame rate calculation
        total += (now := time.perf_counter()) - last
        frames += 1
        last = now

        if frames == 240:
            widget_list["test2"].anchor = (0, 0)

    return (total, frames)


if __name__ == "__main__":
    try:
        total, frames = cur.wrapper(main)
        print("TOTAL FRAMES", frames)
        print(f"TOTAL FRAME TIME {round(total, 3)}s")
        print("AVG FRAME RATE", round(frames / total))
    except (KeyboardInterrupt, EOFError):
        pass
