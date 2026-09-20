#!/usr/bin/env -S python3 -BOO
import cProfile
import curses as cur
import math
import time

from src import general as gen
from src import renderer as ren
from src import widgets as wgts

prof = cProfile.Profile()
total = 0
frames = 0


def start(scr: cur.window) -> list[int]:
    global total, frames

    win = ren.Win(scr)
    widget_list = [
        wgts.MainBox(
            name="main-box",
            height=lambda win, widget: win.term_sz[0],
            width=lambda win, widget: win.term_sz[1],
            anchor=wgts.anchor_centre,
            content=[("hi sneha",), ("hi sneha 2",), ("",), ("",), ("",), ("hi sneha 3",)],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=-1,
            border=True,
            border_type="double",
        ),
        # wgts.MainBox(
        #     name="label",
        #     height=1,
        #     width=lambda win, widget: win.term_sz[1] // 2,
        #     anchor=(1, wgts.anchor_hori_centre),
        #     content=[("MESSENGER",)],
        #     line_range=[0, math.inf],
        #     col_range=[0, math.inf],
        #     alignment=0,
        #     border=False,
        #     border_type=None,
        # ),
        # wgts.ConvoList(
        #     name="convo-list",
        #     height=lambda win, widget: win.term_sz[0],
        #     width=lambda win, widget: win.term_sz[1],
        #     anchor=wgts.anchor_centre,
        #     content=[],
        #     line_range=[0, math.inf],
        #     col_range=[0, math.inf],
        #     alignment=-1,
        #     border=False,
        #     border_type=None,
        # ),
        wgts.ConvoEntry(
            name="convo-entry-1",
            height=4,
            width=lambda win, widget: win.term_sz[1] // 2,
            anchor=(2, 1),
            content=[("USER1")],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=0,
            border=True,
            border_type="rounded",
        ),
    ]

    frame_time = 1 / gen.TARGET_FPS
    last = time.perf_counter()
    prof.enable()

    while True:
        key = win.scr.getch()
        if gen.is_key(key, ("q", "Q")):
            break
        elif key == cur.KEY_RESIZE:
            win.term_sz = win.scr.getmaxyx()
            cur.resize_term(*win.term_sz)
        win.erase()
        win.draw(widget_list)
        # frame rate limiter
        # time.sleep(max(0, frame_time - (time.perf_counter() - last)))
        win.addnstr(1, 1, f"FRAME RATE {round(1 / (time.perf_counter() - last))}", win.term_sz[1])
        win.refresh()

        # for frame rate calculation
        total += (now := time.perf_counter()) - last
        frames += 1
        last = now

    prof.disable()
    return (total, frames)


def main():
    try:
        total, frames = cur.wrapper(start)
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print("TOTAL FRAMES", frames)
        print(f"TOTAL FRAME TIME {round(total, 3)}s")
        print("AVG FRAME RATE", "ud" if frames == 0 else round(frames / total))


if __name__ == "__main__":
    main()
    # cProfile.run("main()", sort="cumulative")
    prof.print_stats(sort="cumulative")
