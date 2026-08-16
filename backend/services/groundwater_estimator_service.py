from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from backend.services.location_service import (
    load_data,
    normalize_name,
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "jala_raksha_groundwater_regressor.pkl"
)

FEATURES_PATH = (
    BASE_DIR
    / "models"
    / "jala_raksha_groundwater_features.pkl"
)


@lru_cache(maxsize=1)
def load_estimator():
    """
    Load the trained groundwater regression model.
    """
    return joblib.load(
        MODEL_PATH
    )


@lru_cache(maxsize=1)
def load_estimator_features():
    """
    Load the exact feature list used during training.
    """
    return joblib.load(
        FEATURES_PATH
    )


def get_location_history(
    district,
    mandal,
):
    """
    Get historical monthly groundwater and rainfall
    data for one district + mandal.
    """

    df = load_data().copy()

    district_key = normalize_name(
        district
    )

    mandal_key = normalize_name(
        mandal
    )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce",
    )

    df["monthly_rainfall_mm_model"] = (
        pd.to_numeric(
            df[
                "monthly_rainfall_mm_model"
            ],
            errors="coerce",
        )
    )

    rows = df[
        (df["district_key"] == district_key)
        &
        (df["mandal_key"] == mandal_key)
    ].copy()

    if rows.empty:
        return None

    monthly = (
        rows.groupby(
            "date",
            as_index=False,
        )
        .agg(
            groundwater=(
                "value",
                "mean",
            ),
            rainfall=(
                "monthly_rainfall_mm_model",
                "mean",
            ),
            lat=(
                "lat",
                "median",
            ),
            lon=(
                "long",
                "median",
            ),
        )
    )

    monthly = monthly.dropna(
        subset=[
            "date",
            "groundwater",
        ]
    )

    monthly = monthly.sort_values(
        "date"
    ).reset_index(
        drop=True
    )

    return monthly


def _season_features(month):
    """
    Generate seasonal features exactly as used
    during training.
    """

    month_sin = np.sin(
        2
        * np.pi
        * month
        / 12
    )

    month_cos = np.cos(
        2
        * np.pi
        * month
        / 12
    )

    return (
        month_sin,
        month_cos,
    )


def _historical_rainfall_for_month(
    history,
    month,
):
    """
    Estimate rainfall for a future month using
    the historical rainfall values for the same
    calendar month.

    Example:
        Future July rainfall
        =
        historical July rainfall average.
    """

    same_month = history[
        history["date"].dt.month
        == month
    ]["rainfall"].dropna()

    if same_month.empty:
        return float(
            history["rainfall"]
            .dropna()
            .mean()
        )

    return float(
        same_month.mean()
    )


def _build_prediction_features(
    history,
    target_date,
):
    """
    Build the exact feature vector required
    by the trained regression model.

    Only information available before target_date
    is used.
    """

    history = history.sort_values(
        "date"
    ).copy()

    groundwater = (
        history["groundwater"]
        .dropna()
        .tolist()
    )

    rainfall = (
        history["rainfall"]
        .dropna()
        .tolist()
    )

    if len(groundwater) < 6:
        raise ValueError(
            "At least 6 historical groundwater "
            "observations are required."
        )

    month = target_date.month
    year = target_date.year

    month_sin, month_cos = (
        _season_features(month)
    )

    future_rainfall = (
        _historical_rainfall_for_month(
            history,
            month,
        )
    )

    rain_lag_1 = (
        rainfall[-1]
        if len(rainfall) >= 1
        else future_rainfall
    )

    rain_lag_2 = (
        rainfall[-2]
        if len(rainfall) >= 2
        else rain_lag_1
    )

    rain_lag_3 = (
        rainfall[-3]
        if len(rainfall) >= 3
        else rain_lag_2
    )

    rain_history_3 = (
        rainfall[-3:]
        if len(rainfall) >= 3
        else rainfall
    )

    rain_history_6 = (
        rainfall[-6:]
        if len(rainfall) >= 6
        else rainfall
    )

    gw_history_3 = (
        groundwater[-3:]
    )

    gw_history_6 = (
        groundwater[-6:]
    )

    lat = float(
        history["lat"].dropna().median()
    )

    lon = float(
        history["lon"].dropna().median()
    )

    year_index = (
        year
        - int(
            history["date"]
            .dt.year
            .min()
        )
    )

    features = {
        "lat": lat,
        "lon": lon,
        "month": month,
        "month_sin": month_sin,
        "month_cos": month_cos,
        "year_index": year_index,
        "rainfall": future_rainfall,
        "rain_lag_1": rain_lag_1,
        "rain_lag_2": rain_lag_2,
        "rain_lag_3": rain_lag_3,
        "rain_3month_avg": float(
            np.mean(
                rain_history_3
            )
        ),
        "rain_6month_avg": float(
            np.mean(
                rain_history_6
            )
        ),
        "gw_lag_1": groundwater[-1],
        "gw_lag_2": groundwater[-2],
        "gw_lag_3": groundwater[-3],
        "gw_3month_avg": float(
            np.mean(
                gw_history_3
            )
        ),
        "gw_6month_avg": float(
            np.mean(
                gw_history_6
            )
        ),
    }

    expected_features = (
        load_estimator_features()
    )

    return pd.DataFrame(
        [
            {
                feature: features[
                    feature
                ]
                for feature in expected_features
            }
        ]
    )


def estimate_present_groundwater(
    district,
    mandal,
    target_date=None,
):
    """
    Estimate the groundwater level for the
    requested present/current date.

    The model recursively predicts every missing
    month between the last real observation and
    the target date.

    This means the system does NOT simply use
    the old 2023 observation as the current value.
    """

    history = get_location_history(
        district,
        mandal,
    )

    if history is None or history.empty:
        return None

    history = history.copy()

    history["date"] = pd.to_datetime(
        history["date"]
    )

    last_observation_date = (
        history["date"].max()
    )

    if target_date is None:
        target_date = pd.Timestamp(
            pd.Timestamp.now().year,
            pd.Timestamp.now().month,
            1,
        )
    else:
        target_date = pd.Timestamp(
            target_date
        )

        target_date = pd.Timestamp(
            target_date.year,
            target_date.month,
            1,
        )

    # If target is already covered by the
    # historical dataset, return that observation.
    if target_date <= last_observation_date:

        existing = history[
            history["date"]
            == target_date
        ]

        if not existing.empty:

            value = float(
                existing[
                    "groundwater"
                ].iloc[0]
            )

            return {
                "district": normalize_name(
                    district
                ),
                "mandal": normalize_name(
                    mandal
                ),
                "estimated_groundwater_m": round(
                    value,
                    3,
                ),
                "target_date": target_date.strftime(
                    "%Y-%m-%d"
                ),
                "last_observation_date": (
                    last_observation_date.strftime(
                        "%Y-%m-%d"
                    )
                ),
                "historical_observations": int(
                    len(history)
                ),
                "estimated": False,
                "method": (
                    "Historical observation"
                ),
            }

    model = load_estimator()

    current_history = history[
        [
            "date",
            "groundwater",
            "rainfall",
            "lat",
            "lon",
        ]
    ].copy()

    future_dates = pd.date_range(
        start=(
            last_observation_date
            + pd.DateOffset(
                months=1
            )
        ),
        end=target_date,
        freq="MS",
    )

    if len(future_dates) == 0:
        return None

    predictions = []

    for future_date in future_dates:

        X = _build_prediction_features(
            current_history,
            future_date,
        )

        prediction = float(
            model.predict(X)[0]
        )

        # Groundwater depth cannot be negative.
        prediction = max(
            0.0,
            prediction,
        )

        future_rainfall = (
            _historical_rainfall_for_month(
                current_history,
                future_date.month,
            )
        )

        lat = float(
            current_history[
                "lat"
            ].dropna().median()
        )

        lon = float(
            current_history[
                "lon"
            ].dropna().median()
        )

        new_row = pd.DataFrame(
            [
                {
                    "date": future_date,
                    "groundwater": prediction,
                    "rainfall": future_rainfall,
                    "lat": lat,
                    "lon": lon,
                }
            ]
        )

        current_history = pd.concat(
            [
                current_history,
                new_row,
            ],
            ignore_index=True,
        )

        predictions.append(
            {
                "date": future_date.strftime(
                    "%Y-%m-%d"
                ),
                "predicted_groundwater_m": round(
                    prediction,
                    3,
                ),
            }
        )

    final_prediction = (
        predictions[-1]
    )

    return {
        "district": normalize_name(
            district
        ),
        "mandal": normalize_name(
            mandal
        ),
        "estimated_groundwater_m": (
            final_prediction[
                "predicted_groundwater_m"
            ]
        ),
        "target_date": final_prediction[
            "date"
        ],
        "last_observation_date": (
            last_observation_date.strftime(
                "%Y-%m-%d"
            )
        ),
        "historical_observations": int(
            len(history)
        ),
        "forecast_steps": len(
            predictions
        ),
        "estimated": True,
        "method": (
            "Random Forest recursive "
            "historical groundwater estimation"
        ),
        "forecast": predictions,
    }