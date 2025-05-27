"""
Keyboard Utilities
Helper functions for building keyboard layouts.
"""

# --------------------------------------------------------------------------------

from aiogram.types import KeyboardButton

# --------------------------------------------------------------------------------

def make_k_from_list(items: list[str]) -> list[list[KeyboardButton]]:
    """
    Build keyboard layout from list of strings.

    Args:
        items (list[str]): List of button labels.

    Returns:
        list[list[KeyboardButton]]: 2D list of KeyboardButton rows.
    """
    buttons = [KeyboardButton(text=el) for el in items]
    result: list[list[KeyboardButton]] = [[]]
    row = 0
    for btn in buttons:
        if len(result[row]) == 3:
            result.append([])
            row += 1
        result[row].append(btn)
    return result
