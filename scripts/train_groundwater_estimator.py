from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "interim"
    / "jala_raksha_model_data.csv"
)

MODELS_DIR = BASE_DIR / "models"

MODEL_PATH = (
    MODELS_DIR
    / "jala_raksha_groundwater_regressor.pkl"
)

FEATURES_PATH = (
    MODELS_DIR
    / "jala_raksha_groundwater_features.pkl"
)


def load_monthly_data():
    """
    Load historical groundwater and rainfall data
    and aggregate multiple observations into one
    monthly value per district + mandal.
    """

    df = pd.read_csv(DATA_PATH)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce",
    )

    df["monthly_rainfall_mm_model"] = pd.to_numeric(
        df["monthly_rainfall_mm_model"],
        errors="coerce",
    )

    df["lat"] = pd.to_numeric(
        df["lat"],
        errors="coerce",
    )

    df["long"] = pd.to_numeric(
        df["long"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "date",
            "value",
            "district_key",
            "mandal_key",
        ]
    )

    monthly = (
        df.groupby(
            [
                "district_key",
                "mandal_key",
                "date",
            ],
            as_index=False,
        )
        .agg(
            groundwater=("value", "mean"),
            rainfall=(
                "monthly_rainfall_mm_model",
                "mean",
            ),
            lat=("lat", "median"),
            lon=("long", "median"),
        )
    )

    monthly["year"] = (
        monthly["date"].dt.year
    )

    monthly["month"] = (
        monthly["date"].dt.month
    )

    monthly = monthly.sort_values(
        [
            "district_key",
            "mandal_key",
            "date",
        ]
    ).reset_index(drop=True)

    return monthly


def add_features(df):
    """
    Create historical groundwater and rainfall
    features.

    All lag and rolling features use only previous
    observations so the current target value is not
    used to predict itself.
    """

    df = df.copy()

    group_columns = [
        "district_key",
        "mandal_key",
    ]

    grouped = df.groupby(
        group_columns,
        sort=False,
    )

    # -------------------------------------------------
    # Previous groundwater observations
    # -------------------------------------------------

    df["gw_lag_1"] = (
        grouped["groundwater"]
        .shift(1)
    )

    df["gw_lag_2"] = (
        grouped["groundwater"]
        .shift(2)
    )

    df["gw_lag_3"] = (
        grouped["groundwater"]
        .shift(3)
    )

    # -------------------------------------------------
    # Previous rainfall observations
    # -------------------------------------------------

    df["rain_lag_1"] = (
        grouped["rainfall"]
        .shift(1)
    )

    df["rain_lag_2"] = (
        grouped["rainfall"]
        .shift(2)
    )

    df["rain_lag_3"] = (
        grouped["rainfall"]
        .shift(3)
    )

    # -------------------------------------------------
    # Historical groundwater rolling averages
    # -------------------------------------------------

    df["gw_3month_avg"] = (
        df.groupby(
            group_columns,
            sort=False,
        )["groundwater"]
        .transform(
            lambda series: (
                series
                .shift(1)
                .rolling(
                    window=3,
                    min_periods=3,
                )
                .mean()
            )
        )
    )

    df["gw_6month_avg"] = (
        df.groupby(
            group_columns,
            sort=False,
        )["groundwater"]
        .transform(
            lambda series: (
                series
                .shift(1)
                .rolling(
                    window=6,
                    min_periods=6,
                )
                .mean()
            )
        )
    )

    # -------------------------------------------------
    # Historical rainfall rolling averages
    # -------------------------------------------------

    df["rain_3month_avg"] = (
        df.groupby(
            group_columns,
            sort=False,
        )["rainfall"]
        .transform(
            lambda series: (
                series
                .shift(1)
                .rolling(
                    window=3,
                    min_periods=3,
                )
                .mean()
            )
        )
    )

    df["rain_6month_avg"] = (
        df.groupby(
            group_columns,
            sort=False,
        )["rainfall"]
        .transform(
            lambda series: (
                series
                .shift(1)
                .rolling(
                    window=6,
                    min_periods=6,
                )
                .mean()
            )
        )
    )

    # -------------------------------------------------
    # Seasonal features
    # -------------------------------------------------

    df["month_sin"] = np.sin(
        2
        * np.pi
        * df["month"]
        / 12
    )

    df["month_cos"] = np.cos(
        2
        * np.pi
        * df["month"]
        / 12
    )

    # -------------------------------------------------
    # Historical time progression
    # -------------------------------------------------

    df["year_index"] = (
        df["year"]
        - df["year"].min()
    )

    return df


def build_training_data(monthly):
    """
    Build the final regression training dataset.
    """

    df = add_features(
        monthly
    )

    features = [
        "lat",
        "lon",
        "month",
        "month_sin",
        "month_cos",
        "year_index",
        "rainfall",
        "rain_lag_1",
        "rain_lag_2",
        "rain_lag_3",
        "rain_3month_avg",
        "rain_6month_avg",
        "gw_lag_1",
        "gw_lag_2",
        "gw_lag_3",
        "gw_3month_avg",
        "gw_6month_avg",
    ]

    df = df.dropna(
        subset=features + [
            "groundwater"
        ]
    ).copy()

    return df, features


def validate_model(
    df,
    features,
):
    """
    Time-aware validation.

    Train:
        2021 + 2022

    Validate:
        2023

    This simulates predicting a future
    period using previous historical data.
    """

    train = df[
        df["year"] < 2023
    ].copy()

    test = df[
        df["year"] == 2023
    ].copy()

    if train.empty:
        raise RuntimeError(
            "Training dataset is empty."
        )

    if test.empty:
        raise RuntimeError(
            "2023 validation dataset is empty."
        )

    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=18,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        train[features],
        train["groundwater"],
    )

    predictions = model.predict(
        test[features]
    )

    mae = mean_absolute_error(
        test["groundwater"],
        predictions,
    )

    rmse = np.sqrt(
        mean_squared_error(
            test["groundwater"],
            predictions,
        )
    )

    r2 = r2_score(
        test["groundwater"],
        predictions,
    )

    print()
    print(
        "=============================="
    )
    print(
        "      2023 VALIDATION"
    )
    print(
        "=============================="
    )

    print(
        f"Training rows  : {len(train)}"
    )

    print(
        f"Validation rows: {len(test)}"
    )

    print(
        f"MAE            : {mae:.3f} m"
    )

    print(
        f"RMSE           : {rmse:.3f} m"
    )

    print(
        f"R2             : {r2:.3f}"
    )

    comparison = test[
        [
            "district_key",
            "mandal_key",
            "date",
            "groundwater",
        ]
    ].copy()

    comparison["predicted"] = (
        predictions
    )

    comparison["absolute_error"] = (
        comparison["groundwater"]
        - comparison["predicted"]
    ).abs()

    moinabad = comparison[
        (
            comparison["district_key"]
            == "RANGAREDDY"
        )
        &
        (
            comparison["mandal_key"]
            == "MOINABAD"
        )
    ]

    if not moinabad.empty:

        print()
        print(
            "=============================="
        )
        print(
            "      MOINABAD 2023"
        )
        print(
            "=============================="
        )

        print(
            moinabad.to_string(
                index=False
            )
        )

        print()

        print(
            "Moinabad MAE:"
        )

        print(
            f"{moinabad['absolute_error'].mean():.3f} m"
        )

    return model


def train_final_model(
    df,
    features,
):
    """
    Train the final groundwater estimator
    using all available historical data.
    """

    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=20,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        df[features],
        df["groundwater"],
    )

    return model


def print_feature_importance(
    model,
    features,
):
    """
    Display feature importance so we can
    understand what the estimator learned.
    """

    importance = pd.DataFrame(
        {
            "feature": features,
            "importance": (
                model.feature_importances_
            ),
        }
    )

    importance = importance.sort_values(
        "importance",
        ascending=False,
    )

    print()
    print(
        "=============================="
    )
    print(
        "    FEATURE IMPORTANCE"
    )
    print(
        "=============================="
    )

    print(
        importance.to_string(
            index=False
        )
    )


def main():

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Loading historical data..."
    )

    monthly = load_monthly_data()

    print(
        f"Monthly rows: {len(monthly)}"
    )

    print(
        "Building historical features..."
    )

    df, features = (
        build_training_data(
            monthly
        )
    )

    print(
        "Training rows after features: "
        f"{len(df)}"
    )

    print()
    print(
        "Validating model..."
    )

    validate_model(
        df,
        features,
    )

    print()
    print(
        "Training final model..."
    )

    model = train_final_model(
        df,
        features,
    )

    print_feature_importance(
        model,
        features,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    joblib.dump(
        features,
        FEATURES_PATH,
    )

    print()
    print(
        "=============================="
    )
    print(
        "       MODEL SAVED"
    )
    print(
        "=============================="
    )

    print(
        f"Regressor : {MODEL_PATH}"
    )

    print(
        f"Features  : {FEATURES_PATH}"
    )


if __name__ == "__main__":
    main()