from datetime import datetime, timedelta


def calculate_period(last_period_str, cycle_length, period_length):
    """
    Takes period data and returns a dictionary of formatted results.
    """
    # Convert string to datetime object
    last_period = datetime.strptime(last_period_str, "%Y-%m-%d")

    # Core Calculations
    next_period = last_period + timedelta(days=cycle_length)
    ovulation = next_period - timedelta(days=14)
    fertile_start = ovulation - timedelta(days=5)
    fertile_end = ovulation + timedelta(days=1)

    # Countdown Logic
    today = datetime.today().date()
    days_until = (next_period.date() - today).days
    days_until = max(0, days_until)  # Ensures it doesn't go below 0

    # Package the results for the template
    return {
        "days_countdown": days_until,
        "next_period_date": next_period.strftime("%B %d, %Y"),
        "next_period_weekday": next_period.strftime("%A"),
        "ovulation_date": ovulation.strftime("%B %d, %Y"),
        "ovulation_weekday": ovulation.strftime("%A"),
        "fertile_window": f"{fertile_start.strftime('%b %d')} – {fertile_end.strftime('%b %d, %Y')}",
        "most_fertile": ovulation.strftime("%b %d"),
        "cycle_length": cycle_length,
        "period_length": period_length,
    }
