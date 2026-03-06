from datetime import datetime, timedelta
from utilities.helper import parse_date

# Constants for calculations
OVULATION_OFFSET = 14
FERTILE_WINDOW_START = 5
FERTILE_WINDOW_END = 1


def calculate_period(
    last_period_str: str, cycle_length: int, period_length: int
) -> dict:
    """
    Calculate period-related dates and return a dictionary of results.

    Args:
        - last_period_str (str): The start date of the last period in "YYYY-MM-DD" format.
        - cycle_length (int): The average length of the menstrual cycle in days.
        - period_length (int): The average length of the period in days.

    Returns:
        - dict: A dictionary containing calculated dates and information.
    """
    # Convert string to datetime object
    last_period = parse_date(last_period_str)

    # Core Calculations
    next_period = last_period + timedelta(days=cycle_length)
    ovulation = next_period - timedelta(days=OVULATION_OFFSET)
    fertile_start = ovulation - timedelta(days=FERTILE_WINDOW_START)
    fertile_end = ovulation + timedelta(days=FERTILE_WINDOW_END)

    # Countdown Logic
    today = datetime.today().date()
    days_until = max(0, (next_period.date() - today).days)

    # Format dates for display
    next_period_formatted = next_period.strftime("%B %d, %Y")
    next_period_weekday = next_period.strftime("%A")
    ovulation_formatted = ovulation.strftime("%B %d, %Y")
    ovulation_weekday = ovulation.strftime("%A")
    fertile_window = (
        f"{fertile_start.strftime('%b %d')} – {fertile_end.strftime('%b %d, %Y')}"
    )
    most_fertile = ovulation.strftime("%b %d")

    # Package the results for the template
    return {
        "days_countdown": days_until,
        "next_period_date": next_period_formatted,
        "next_period_weekday": next_period_weekday,
        "ovulation_date": ovulation_formatted,
        "ovulation_weekday": ovulation_weekday,
        "fertile_window": fertile_window,
        "most_fertile": most_fertile,
        "cycle_length": cycle_length,
        "period_length": period_length,
    }
