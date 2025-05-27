"""
Validation utilities
Helpers for number and time format validation.
"""

# --------------------------------------------------------------------------------


async def is_number_in_range(s: str) -> bool:
    """
    Check if the given string can be converted to a float.

    Args:
        s (str): Input string to validate.

    Returns:
        bool: True if string represents a number, False otherwise.
    """
    try:
        num = float(s)
        return True
    except ValueError:
        return False


def is_valid_time_format(time_str: str) -> bool:
    """
    Validate if the time string is in correct HH:MM format.

    Args:
        time_str (str): Time string to validate.

    Returns:
        bool: True if time is in valid format, False otherwise.
    """
    if not time_str or ':' not in time_str:
        return False

    try:
        hours, minutes = map(int, time_str.split(':'))
        return 0 <= hours <= 23 and 0 <= minutes <= 59
    except (ValueError, IndexError):
        return False
