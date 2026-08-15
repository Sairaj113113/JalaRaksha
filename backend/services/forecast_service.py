from functools import lru_cache

import numpy as np
import pandas as pd

from backend.services.location_service import (
    load_data,
    normalize_name,
)


FORECAST_MONTHS = 6


@lru_cache(maxsize=1)
def get_forecast_data():
    """
    Prepare historical groundwater data for forecasting.
    """
    df = load_data().copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["date", "value"]
    )

    return df


def get_location_history(
    district,
    mandal,
):
    """
    Get historical groundwater observations
    for one district + mandal.
    """
    df = get_forecast_data()

    district_key = normalize_name(
        district
    )

    mandal_key = normalize_name(
        mandal
    )

    rows = df[
        (df["district_key"] == district_key)
        & (df["mandal_key"] == mandal_key)
    ].copy()

    if rows.empty:
        return None

    rows = rows.sort_values(
        "date"
    )

    return rows


def _linear_forecast(
    values,
    periods,
):
    """
    Simple linear trend forecast.

    Used as a transparent baseline forecast
    rather than pretending that the Random Forest
    classification model is a time-series model.
    """
    values = np.asarray(
        values,
        dtype=float,
    )

    if len(values) == 0:
        return []

    if len(values) == 1:
        return [
            float(values[-1])
            for _ in range(periods)
        ]

    x = np.arange(
        len(values),
        dtype=float,
    )

    slope, intercept = np.polyfit(
        x,
        values,
        1,
    )

    future_x = np.arange(
        len(values),
        len(values) + periods,
        dtype=float,
    )

    predictions = (
        intercept
        + slope * future_x
    )

    return [
        max(0.0, float(value))
        for value in predictions
    ]


def forecast_location(
    district,
    mandal,
    periods=FORECAST_MONTHS,
):
    """
    Forecast future groundwater values
    for a district + mandal.
    """

    if periods < 1:
        raise ValueError(
            "Forecast periods must be at least 1."
        )

    if periods > 12:
        raise ValueError(
            "Forecast periods cannot exceed 12 months."
        )

    history = get_location_history(
        district,
        mandal,
    )

    if history is None or history.empty:
        return None

    monthly = (
        history
        .set_index("date")["value"]
        .resample("MS")
        .mean()
        .dropna()
    )

    if monthly.empty:
        return None

    values = monthly.values

    forecast_values = _linear_forecast(
        values,
        periods,
    )

    last_date = monthly.index[-1]

    forecast = []

    for index, value in enumerate(
        forecast_values,
        start=1,
    ):
        future_date = (
            last_date
            + pd.DateOffset(
                months=index
            )
        )

        forecast.append(
            {
                "date": future_date.strftime(
                    "%Y-%m-%d"
                ),
                "predicted_groundwater_m": round(
                    value,
                    3,
                ),
            }
        )

    return {
        "district": district_key_name(
            history
        ),
        "mandal": mandal_key_name(
            history
        ),
        "historical_observations": int(
            len(history)
        ),
        "historical_months": int(
            len(monthly)
        ),
        "last_observation_date": (
            last_date.strftime(
                "%Y-%m-%d"
            )
        ),
        "forecast_months": periods,
        "forecast": forecast,
    }


def district_key_name(history):
    """
    Return a clean district name from history.
    """
    value = history["district_key"].iloc[0]

    return str(value)


def mandal_key_name(history):
    """
    Return a clean mandal name from history.
    """
    value = history["mandal_key"].iloc[0]

    return str(value)