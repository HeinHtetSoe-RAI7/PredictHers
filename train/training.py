# import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# import joblib


# def train_with_avg_length(csv_filepath):
#     # 1. Load and sort the dataset chronologically per user
#     df = pd.read_csv(csv_filepath)
#     # df = df.`sort_values(by=["user_id", "date"])

#     # 2. Create the past cycle features (2 gaps from 3 dates)
#     df["prev_cycle_1"] = df.groupby("user_id")["cycle"].shift(
#         1
#     )  # Most recent past cycle
#     df["prev_cycle_2"] = df.groupby("user_id")["cycle"].shift(
#         2
#     )  # The cycle before that

#     # 3. Pull the past 3 bleeding lengths to calculate the average
#     df["prev_length_1"] = df.groupby("user_id")["period_length"].shift(1)
#     df["prev_length_2"] = df.groupby("user_id")["period_length"].shift(2)
#     df["prev_length_3"] = df.groupby("user_id")["period_length"].shift(3)

#     # Calculate the average length feature
#     df["avg_length"] = (
#         df["prev_length_1"] + df["prev_length_2"] + df["prev_length_3"]
#     ) / 3

#     # 4. Clean up rows that don't have enough history yet
#     df_train = df.dropna(subset=["prev_cycle_2", "avg_length"])

#     # 5. Define Features (X) and Target (y)
#     # Notice we now only have 5 features total
#     features = ["bmi", "age", "prev_cycle_1", "prev_cycle_2", "avg_length"]
#     X = df_train[features]
#     y = df_train["cycle"]  # Predicting the next cycle

#     # 6. Train and Save
#     model = RandomForestRegressor(n_estimators=100, random_state=42)
#     model.fit(X, y)

#     joblib.dump(model, "menstrual_rf_model_avg_length.pkl")
#     print(f"Model trained on {len(df_train)} rows using average length, and saved!")


# train_with_avg_length("menstrual_data.csv")

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib


def train_universal_model(csv_filepath="menstrual_data.csv"):
    print("Loading and cleaning data...")
    df = pd.read_csv(csv_filepath)
    df.columns = df.columns.str.strip()
    df["date"] = pd.to_datetime(df["date"])

    # Sort chronologically per user
    df = df.sort_values(by=["user_id", "date"])

    # 1. Calculate actual cycle length (the Target we want to predict)
    df["target_cycle"] = df.groupby("user_id")["date"].diff().dt.days

    # 2. Shift to get the previous cycles (so the model doesn't cheat by looking at the future)
    df["prev_cycle_1"] = df.groupby("user_id")["target_cycle"].shift(1)
    df["prev_cycle_2"] = df.groupby("user_id")["target_cycle"].shift(2)

    # 3. Calculate "All-Time" personalized stats up to that specific row
    # We use 'prev_cycle_1' here to prevent data leakage (the model can't know the target yet)
    df["all_time_avg_cycle"] = df.groupby("user_id")["prev_cycle_1"].transform(
        lambda x: x.expanding().mean()
    )
    df["cycle_std_dev"] = df.groupby("user_id")["prev_cycle_1"].transform(
        lambda x: x.expanding().std()
    )

    # If they only have 1 past cycle, standard deviation is NaN. We fill it with 0.
    df["cycle_std_dev"] = df["cycle_std_dev"].fillna(0)

    # Calculate expanding average of their period bleeding length
    df["avg_period_length"] = (
        df.groupby("user_id")["period_length"]
        .shift(1)
        .transform(lambda x: x.expanding().mean())
    )

    # 4. Clean up the dataset
    # Drop rows that don't have enough history to form our baseline features
    train_df = df.dropna(
        subset=["prev_cycle_2", "all_time_avg_cycle", "avg_period_length"]
    )

    # 5. Define our 7 universal features
    features = [
        "bmi",
        "age",
        "prev_cycle_1",
        "prev_cycle_2",
        "all_time_avg_cycle",
        "cycle_std_dev",
        "avg_period_length",
    ]

    X = train_df[features]
    y = train_df["target_cycle"]

    # 6. Train the Random Forest
    print(f"Training Universal Random Forest on {len(train_df)} historical cycles...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X, y)

    # 7. Save the model
    joblib.dump(model, "models/universal_menstrual_model.pkl")
    print("Success! Saved as 'universal_menstrual_model.pkl'")


if __name__ == "__main__":
    train_universal_model()
