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
        "main-box": wgts.MainBox(
            height=lambda win, widget: win.term_sz[0],
            width=lambda win, widget: win.term_sz[1],
            anchor=wgts.anchor_centre,
            content=[],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=-1,
            border=True,
        ),
        "convo-list": wgts.ConvoList(
            height=lambda win, widget: win.term_sz[0] - 4,
            width=lambda win, widget: win.term_sz[1] - 4,
            anchor=wgts.anchor_centre,
            content=[],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=-1,
            border=True,
        ),
        "convo-entry": wgts.ConvoEntry(
            height=4,
            width=lambda win, widget: win.term_sz[1] - 6,
            anchor=(3, 3),
            content=[("sneha", cur.A_REVERSE), ("Hi Thiru",)],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=-1,
            border=True,
        ),
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

    return (total, frames)


if __name__ == "__main__":
    try:
        total, frames = cur.wrapper(main)
        print("TOTAL FRAMES", frames)
        print(f"TOTAL FRAME TIME {round(total, 3)}s")
        print("AVG FRAME RATE", round(frames / total))
    except (KeyboardInterrupt, EOFError):
        pass
