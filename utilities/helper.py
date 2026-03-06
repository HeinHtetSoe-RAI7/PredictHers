from datetime import datetime


def parse_int(value: str, default=None):
    """Convert a string to an integer, or return a default value if invalid."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def parse_float(value: str, default=None):
    """Convert a string to a float, or return a default value if invalid."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_date(date_str: str) -> datetime:
    """
    Parse a date string in 'YYYY-MM-DD' format into a datetime object.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected 'YYYY-MM-DD'.")
