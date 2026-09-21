#!/usr/bin/env -S python3 -BOO
import cProfile
import curses as cur
import datetime as dt
import io
import math
import pstats
import time

from src import general as gen
from src import renderer as ren
from src import widgets as wgts

total = 0
frames = 0
prof = cProfile.Profile()


def start(scr: cur.window) -> list[int]:
    global total, frames

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
            border_type="double",
        ),
        "label": wgts.MainBox(
            height=1,
            width=lambda win, widget: win.term_sz[1] // 2,
            anchor=(1, wgts.anchor_hori_centre),
            content=[("MESSENGER",)],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=0,
            border=False,
            border_type=None,
        ),
        "convo-list": wgts.ConvoList(
            height=lambda win, widget: win.term_sz[0],
            width=lambda win, widget: win.term_sz[1],
            anchor=wgts.anchor_centre,
            content=[],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=-1,
            border=False,
            border_type=None,
        ),
        "convo-entry-1": wgts.ConvoEntry(
            height=4,
            width=lambda win, widget: win.term_sz[1] // 2,
            anchor=(2, 1),
            content=[("USER1", cur.A_REVERSE), ("Hello world, this is a test message!",)],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
            alignment=0,
            border=True,
            border_type="rounded",
        ),
    }

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
        if frames == 10000:
            break

    prof.disable()
    return (total, frames)


def main():
    global total, frames
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
    s = io.StringIO()
    ps = pstats.Stats(prof, stream=s).sort_stats("cumulative")
    ps.print_stats()
    filename = f"prof-{dt.datetime.now().strftime("%Y%m%d-%H%M%S")}.cprof"
    with open(filename, "w+") as f:
        f.write(s.getvalue())
    print(f"Wrote profiler output to {filename}")
