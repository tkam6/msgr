#!/usr/bin/env -S python3 -BOO
import curses as cur
import math

from src import general as gen
from src import renderer as ren
from src import widgets as wgts


def main(scr: cur.window) -> None:
    win = ren.Win(scr)
    widget_list = {
        "test": wgts.MainBox(
            width=win.term_sz[1],
            height=win.term_sz[0],
            anchor=(0, 0),
            content=[
                "hello world, this is thiru from nitc. im really stupid, and i'm writing this stupidly long sentence to test out my new messenger application program im writing right now, right fucking now.",
                "hello wold, this is thiru from nitc. im really stupid, and i'm writing this stupidly long sentence to test out my new messenger application program im writing right now, right fucking now.",
                "llo wold, this thiru from nitc. im really stupid, and i'm writing this stupidly long sentence to test out my new messenger application program im writing right now, right fucking now.",
            ],
            line_range=[0, math.inf],
            col_range=[0, math.inf],
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
