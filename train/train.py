import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit, cross_validate
from sklearn.metrics import mean_absolute_error
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
csv_path = BASE_DIR.parent / "dataset" / "menstrual_data.csv"
model_export_path = BASE_DIR.parent / "models" / "universal_menstrual_model.pkl"


def prep_clean_rf_data(csv_filepath=csv_path):
    """Load, clean, and prepare the dataset for Random Forest training."""
    df = pd.read_csv(csv_filepath)
    print(f"\nOriginal dataset loaded: {len(df)} records.\n")

    df.columns = df.columns.str.strip()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by=["user_id", "date"])
    print(df.head())

    # Outlier filtering
    df.rename(columns={"prev_cycle": "prev_cycle_1"}, inplace=True)
    df = df[(df["cycle"] >= 15) & (df["cycle"] <= 60)]
    df = df[(df["prev_cycle_1"] >= 15) & (df["prev_cycle_1"] <= 60)]
    print(f"\nDataset after outlier filtering: {len(df)} records.\n")

    # Feature engineering
    df["prev_cycle_2"] = df.groupby("user_id")["prev_cycle_1"].shift(1)
    df["all_time_avg_cycle"] = df.groupby("user_id")["prev_cycle_1"].transform(
        lambda x: x.expanding().mean()
    )
    df["cycle_std_dev"] = (
        df.groupby("user_id")["prev_cycle_1"]
        .transform(lambda x: x.expanding().std())
        .fillna(0)
    )
    df["avg_period_length"] = (
        df.groupby("user_id")["period_length"]
        .shift(1)
        .transform(lambda x: x.expanding().mean())
    )

    # Clean up NaNs and sort globally for Time Series
    train_df = df.dropna(
        subset=["prev_cycle_2", "all_time_avg_cycle", "avg_period_length"]
    ).copy()
    train_df = train_df.sort_values(by="date")

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
    y = train_df["cycle"]

    return X, y, train_df


def train_and_validate_rf(csv_filepath=csv_path):
    """Main function to train the Random Forest model and validate it using Time Series Split."""
    X, y, train_df = prep_clean_rf_data(csv_filepath)
    print(f"Cleaned dataset ready: {len(X)} records.\n")

    # Show the Baseline to beat
    baseline_mae = mean_absolute_error(y, train_df["all_time_avg_cycle"])
    print(f"Baseline MAE (Just guessing average): {baseline_mae:.4f} days\n")

    # Initialize Random Forest and Time Series Split
    rf = RandomForestRegressor(random_state=42)
    tscv = TimeSeriesSplit(n_splits=6)

    # Hyperparameter grid
    param_grid = {
        "n_estimators": [50, 100, 150, 200],
        "max_depth": [3, 4, 5, 6],
        "min_samples_split": [2, 5, 10, 20],
        "min_samples_leaf": [2, 4, 6, 8],
        "max_features": ["sqrt", "log2", 1.0, 0.5, 0.7],
    }

    print(
        "Tuning Random Forest with Time Series Split (this might take 10-20 seconds)..."
    )
    search = RandomizedSearchCV(
        rf,
        param_distributions=param_grid,
        n_iter=20,
        scoring="neg_mean_absolute_error",
        cv=tscv,
        random_state=42,
        n_jobs=-1,
    )

    search.fit(X, y)
    best_model = search.best_estimator_

    print("=== BEST HYPERPARAMETERS FOUND ===")
    print(search.best_params_)

    print("\nRunning final Time Series validation on Best Model...")
    scoring_metrics = {
        "mae": "neg_mean_absolute_error",
        "rmse": "neg_root_mean_squared_error",
        "r2": "r2",
    }

    cv_results = cross_validate(best_model, X, y, cv=tscv, scoring=scoring_metrics)

    mae_scores = -cv_results["test_mae"]
    rmse_scores = -cv_results["test_rmse"]
    r2_scores = cv_results["test_r2"]

    print("=== FINAL RANDOM FOREST VALIDATION RESULTS ===")
    print(f"Average MAE:  {np.mean(mae_scores):.4f} days")
    print(f"Average RMSE: {np.mean(rmse_scores):.4f} days")
    print(f"Average R2:   {np.mean(r2_scores):.4f}")

    # Export the best model
    export_model(best_model)


def export_model(model, file_path=model_export_path):
    """
    Save the trained model to the specified file path.
    """
    joblib.dump(model, file_path)
    print(f"\nModel saved as '{file_path}'")


if __name__ == "__main__":
    train_and_validate_rf()
