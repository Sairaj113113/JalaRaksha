from datetime import datetime

import numpy as np
import pandas as pd

from backend.services.groundwater_estimator_service import (
    estimate_present_groundwater,
)
from backend.services.location_service import (
    load_data,
    normalize_name,
)


def build_current_observation(
    district,
    mandal,
):
    """
    Build a model-ready observation representing
    the estimated current groundwater condition.

    Groundwater value comes from the historical
    groundwater estimator.

    Current-month rainfall features are estimated
    from historical rainfall behavior for the
    target calendar month.
    """

    district_key = normalize_name(
        district
    )

    mandal_key = normalize_name(
        mandal
    )

    estimate = estimate_present_groundwater(
        district_key,
        mandal_key,
    )

    if estimate is None:
        return None

    target_date = pd.Timestamp(
        estimate["target_date"]
    )

    target_year = target_date.year
    target_month = target_date.month

    df = load_data().copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    df["monthly_rainfall_mm_model"] = (
        pd.to_numeric(
            df["monthly_rainfall_mm_model"],
            errors="coerce",
        )
    )

    df["rainfall_days"] = pd.to_numeric(
        df["rainfall_days"],
        errors="coerce",
    )

    rows = df[
        (df["district_key"] == district_key)
        &
        (df["mandal_key"] == mandal_key)
    ].copy()

    if rows.empty:
        return None

    # Historical observations for the target
    # calendar month.
    month_rows = rows[
        rows["date"].dt.month
        == target_month
    ].copy()

    if month_rows.empty:
        month_rows = rows.copy()

    rainfall = float(
        month_rows[
            "monthly_rainfall_mm_model"
        ]
        .dropna()
        .mean()
    )

    rainfall_days = float(
        month_rows[
            "rainfall_days"
        ]
        .dropna()
        .mean()
    )

    # Use historical values to determine the
    # typical rainfall condition for this month.
    historical_rainfall = (
        rows[
            "monthly_rainfall_mm_model"
        ]
        .dropna()
    )

    rainfall_mean = float(
        historical_rainfall.mean()
    )

    rainfall_std = float(
        historical_rainfall.std()
    )

    if rainfall_std > 0:
        rainfall_deficit_flag = int(
            rainfall
            < (
                rainfall_mean
                - rainfall_std
            )
        )

        heavy_rainfall_flag = int(
            rainfall
            >
            (
                rainfall_mean
                + rainfall_std
            )
        )
    else:
        rainfall_deficit_flag = 0
        heavy_rainfall_flag = 0

    # Historical location coordinates.
    lat = float(
        rows["lat"]
        .dropna()
        .median()
    )

    lon = float(
        rows["long"]
        .dropna()
        .median()
    )

    station_distance = float(
        rows[
            "station_distance_km"
        ]
        .dropna()
        .median()
    )

    coordinate_quality = int(
        rows[
            "coordinate_quality"
        ]
        .dropna()
        .median()
    )

    rainfall_available = int(
        month_rows[
            "rainfall_available"
        ]
        .dropna()
        .max()
        if "rainfall_available" in month_rows
        else 1
    )

    month_sin = np.sin(
        2
        * np.pi
        * target_month
        / 12
    )

    month_cos = np.cos(
        2
        * np.pi
        * target_month
        / 12
    )

    # August is part of the monsoon period.
    # Use the historical dataset's value when
    # available for this calendar month.
    monsoon_values = (
        month_rows[
            "monsoon_month"
        ]
        .dropna()
    )

    if not monsoon_values.empty:
        monsoon_month = int(
            monsoon_values.mode().iloc[0]
        )
    else:
        monsoon_month = int(
            1
            if target_month
            in [6, 7, 8, 9]
            else 0
        )

    observation = {
        "district_key": district_key,
        "mandal_key": mandal_key,
        "date": target_date,
        "value": float(
            estimate[
                "estimated_groundwater_m"
            ]
        ),
        "lat": lat,
        "long": lon,
        "year": target_year,
        "month": target_month,
        "station_distance_km": station_distance,
        "rainfall_available": rainfall_available,
        "rainfall_days": int(
            round(rainfall_days)
        ),
        "monthly_rainfall_mm_model": rainfall,
        "rainfall_deficit_flag": (
            rainfall_deficit_flag
        ),
        "heavy_rainfall_flag": (
            heavy_rainfall_flag
        ),
        "monsoon_month": monsoon_month,
        "month_sin": month_sin,
        "month_cos": month_cos,
        "coordinate_quality": coordinate_quality,
        "rainfall_confidence": (
            "Historical seasonal estimate"
        ),
        "rainfall_estimated": True,
        "groundwater_estimated": True,
        "last_real_observation_date": (
            estimate[
                "last_observation_date"
            ]
        ),
    }

    return observation