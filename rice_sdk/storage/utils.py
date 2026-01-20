from typing import Union


def to_long(val: Union[int, str]) -> int:
    """
    Converts a value to a 64-bit integer (Long).
    """
    if isinstance(val, int):
        return val
    try:
        return int(val)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid value for Long: {val}")
