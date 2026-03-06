from datetime import datetime, timedelta


def calculate_tracker(months, period_length):
    """
    Takes cycle history and returns a dictionary of formatted results.
    """
    # Convert strings to datetime objects
    m1, m2, m3 = months
    d1 = datetime.strptime(m1, "%Y-%m-%d")
    d2 = datetime.strptime(m2, "%Y-%m-%d")
    d3 = datetime.strptime(m3, "%Y-%m-%d")

    # Calculate gaps in days
    gap1 = (d2 - d1).days
    gap2 = (d3 - d2).days

    # Calculate average cycle
    avg_cycle = round((gap1 + gap2) / 2)

    # Fallback if something is wrong
    if avg_cycle <= 0:
        avg_cycle = 28

    # Core Calculations
    next_period = d3 + timedelta(days=avg_cycle)
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
        "cycle_length": avg_cycle,
        "period_length": period_length,
    }
