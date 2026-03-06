import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
from utilities.helper import parse_date


# Constants
OVULATION_OFFSET = 14
FERTILE_WINDOW_START = 5
FERTILE_WINDOW_END = 1
DEFAULT_CYCLE_LENGTH = 28


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def load_and_predict(X_new: pd.DataFrame, fallback: float) -> int:
    """
    Load the model and make predictions. Fallback to the provided value if the model is not found.
    """
    try:
        model = joblib.load("models/universal_menstrual_model.pkl")
        return int(round(model.predict(X_new)[0]))
    except FileNotFoundError:
        return int(round(fallback))


def build_tracker_response(
    last_period_date: datetime, predicted_cycle: int, period_length: float
) -> dict:
    """
    Takes the raw math and turns it into the clean dictionary for frontend template.
    """
    if predicted_cycle <= 0:
        predicted_cycle = DEFAULT_CYCLE_LENGTH

    next_period = last_period_date + timedelta(days=predicted_cycle)
    ovulation = next_period - timedelta(days=OVULATION_OFFSET)
    fertile_start = ovulation - timedelta(days=FERTILE_WINDOW_START)
    fertile_end = ovulation + timedelta(days=FERTILE_WINDOW_END)

    today = datetime.today().date()
    days_until = max(0, (next_period.date() - today).days)

    return {
        "days_countdown": days_until,
        "next_period_date": next_period.strftime("%B %d, %Y"),
        "next_period_weekday": next_period.strftime("%A"),
        "ovulation_date": ovulation.strftime("%B %d, %Y"),
        "ovulation_weekday": ovulation.strftime("%A"),
        "fertile_window": f"{fertile_start.strftime('%b %d')} – {fertile_end.strftime('%b %d, %Y')}",
        "most_fertile": ovulation.strftime("%b %d"),
        "cycle_length": predicted_cycle,
        "period_length": round(period_length, 1),
    }


# ==========================================
# GUEST MODE (Uses the 3 input period dates)
# ==========================================
def predict_with_global_model(
    last_3_dates: list[str], avg_length: float, bmi: float, age: int
) -> dict:
    """
    For users without accounts. Calculates using only their 3 most recent dates.

    Arguments:
        - last_3_dates: List of 3 period start dates (oldest to newest
        - avg_length: Average period bleeding length in days
        - bmi: User's BMI
        - age: User's age

    Returns:
        - Dictionary of results for the frontend template
    """
    # Parse dates
    d1, d2, d3 = map(parse_date, last_3_dates)

    # Calculate recent cycle gaps
    cycle_2 = (d2 - d1).days
    cycle_1 = (d3 - d2).days
    all_time_avg = (cycle_1 + cycle_2) / 2
    cycle_std = (
        np.std([cycle_1, cycle_2], ddof=1) if len([cycle_1, cycle_2]) > 1 else 0.0
    )

    # Prepare features
    X_new = pd.DataFrame(
        [[bmi, age, cycle_1, cycle_2, all_time_avg, cycle_std, avg_length]],
        columns=[
            "bmi",
            "age",
            "prev_cycle_1",
            "prev_cycle_2",
            "all_time_avg_cycle",
            "cycle_std_dev",
            "avg_period_length",
        ],
    )

    # Predict
    predicted_cycle = load_and_predict(X_new, fallback=all_time_avg)
    return build_tracker_response(d3, predicted_cycle, avg_length)


# ==========================================
# PERSONALISED MODE (Uses their whole history)
# ==========================================
def predict_with_personal_history(
    user_id: int,
    manual_last_period_date: str,
    manual_avg_period_length: float = None,
    manual_all_time_avg_cycle: float = None,
    csv_filepath: str = "dataset/menstrual_data.csv",
) -> dict:
    """
    Predicts using user history. Allows overriding specific variables directly from function arguments; otherwise, falls back to CSV data.

    Arguments:
        - user_id: The ID of the user to look up in the CSV
        - manual_last_period_date: The last period date to use for calculations (overrides CSV)
        - manual_avg_period_length: The average period length to use (overrides CSV)
        - manual_all_time_avg_cycle: The average cycle length to use (overrides CSV)
        - csv_filepath: Path to the CSV file containing user data

    Returns:
        - Dictionary of results for the frontend template, or an error message if data is insufficient
    """
    df = pd.read_csv(csv_filepath)
    df.columns = df.columns.str.strip()

    # Filter for the user
    user_data = df[df["user_id"] == user_id].copy()
    if len(user_data) < 3:
        return {
            "error": f"Not enough data for User {user_id}. Need at least 3 periods logged."
        }

    # Parse dates
    user_data["date"] = pd.to_datetime(user_data["date"])
    last_period_date = parse_date(manual_last_period_date)

    # Override logic
    avg_period_length = manual_avg_period_length or user_data["period_length"].mean()
    all_time_avg = manual_all_time_avg_cycle or user_data["cycle"].mean()

    # Extract features
    bmi = user_data["bmi"].iloc[-1]
    age = user_data["age"].iloc[-1]
    cycle_1 = user_data["cycle"].iloc[-1]
    cycle_2 = user_data["cycle"].iloc[-2]
    cycle_std = user_data["cycle"].std() or 0.0

    # Prepare features
    X_new = pd.DataFrame(
        [[bmi, age, cycle_1, cycle_2, all_time_avg, cycle_std, avg_period_length]],
        columns=[
            "bmi",
            "age",
            "prev_cycle_1",
            "prev_cycle_2",
            "all_time_avg_cycle",
            "cycle_std_dev",
            "avg_period_length",
        ],
    )

    # Predict
    predicted_cycle = load_and_predict(X_new, fallback=all_time_avg)
    return build_tracker_response(last_period_date, predicted_cycle, avg_period_length)
