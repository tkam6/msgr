KEYS = {
    "q": ord("q"),
    "Q": ord("Q"),
}


def is_key(key: int, chk_against: tuple[str]) -> bool:
    all_chk_values = (KEYS[i] for i in chk_against)
    return any(key == j for j in all_chk_values)
