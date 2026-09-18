import sys

debug_file = open("./all.log", "a+")

KEYS = {
    "q": ord("q"),
    "Q": ord("Q"),
}
ROUND_CHS = {
    "top-left"    : "╭",
    "top-right"   : "╮",
    "bottom-left" : "╰",
    "bottom-right": "╯",
    "horizontal"  : "─",
    "vertical"    : "│",
}
SHARP_CHS = {
    "top-left"    : "┌",
    "top-right"   : "┐",
    "bottom-left" : "└",
    "bottom-right": "┘",
    "horizontal"  : "─",
    "vertical"    : "│",
}


def is_key(key: int, chk_against: tuple[str]) -> bool:
    all_chk_values = (KEYS[i] for i in chk_against)
    return any(key == j for j in all_chk_values)
