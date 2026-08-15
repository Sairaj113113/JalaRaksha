from functools import lru_cache

import numpy as np
import pandas as pd

from backend.config import (
    GROUNDWATER_DATA_PATH,
    GPS_MAX_DISTANCE_KM,
)


@lru_cache(maxsize=1)
def load_data():
    """
    Load the final Jala Raksha dataset once and reuse it.
    """
    df = pd.read_csv(GROUNDWATER_DATA_PATH)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["district_key"] = (
        df["district_key"]
        .fillna(df["district"])
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["mandal_key"] = (
        df["mandal_key"]
        .fillna(df["mandal"])
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df


def normalize_name(value):
    """
    Normalize district/mandal names for lookup.
    """
    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .upper()
    )


def get_locations():
    """
    Return all available district and mandal combinations.
    """
    df = load_data()

    locations = (
        df[
            [
                "district_key",
                "mandal_key"
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "district_key",
                "mandal_key"
            ]
        )
    )

    result = {}

    for _, row in locations.iterrows():
        district = row["district_key"]
        mandal = row["mandal_key"]

        if district not in result:
            result[district] = []

        result[district].append(mandal)

    return result


def get_latest_observation(district, mandal):
    """
    Get the latest groundwater observation
    for a district + mandal.

    This is the shared observation-selection
    logic used by location, prediction and
    analysis pipelines.
    """
    df = load_data()

    district_key = normalize_name(district)
    mandal_key = normalize_name(mandal)

    rows = df[
        (df["district_key"] == district_key)
        & (df["mandal_key"] == mandal_key)
    ].copy()

    if rows.empty:
        return None

    rows = rows.dropna(
        subset=["date"]
    )

    if rows.empty:
        return None

    latest_date = rows["date"].max()

    latest_rows = rows[
        rows["date"] == latest_date
    ]

    if latest_rows.empty:
        return None

    # Deterministic selection if multiple
    # observations have the same latest date.
    observation = (
        latest_rows
        .sort_values(
            by=[
                "village",
                "value"
            ],
            na_position="last"
        )
        .iloc[0]
        .copy()
    )

    return observation.to_dict()


def _haversine_distance_km(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate great-circle distance between
    two geographic coordinates.
    """
    earth_radius_km = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return (
        2
        * earth_radius_km
        * np.arcsin(np.sqrt(a))
    )


@lru_cache(maxsize=1)
def get_location_points():
    """
    Build unique valid geographic points
    used for GPS location resolution.

    Each point represents a unique
    district + mandal + coordinate combination.
    """
    df = load_data()

    required_columns = [
        "district_key",
        "mandal_key",
        "lat",
        "long",
        "coordinate_source",
        "coordinate_quality",
    ]

    points = df[
        required_columns
    ].copy()

    points["lat"] = pd.to_numeric(
        points["lat"],
        errors="coerce"
    )

    points["long"] = pd.to_numeric(
        points["long"],
        errors="coerce"
    )

    points = points.dropna(
        subset=[
            "lat",
            "long"
        ]
    )

    # Telangana / supported dataset coordinate sanity filter.
    points = points[
        (points["lat"] >= 14)
        & (points["lat"] <= 20)
        & (points["long"] >= 77)
        & (points["long"] <= 82)
    ]

    points = points.drop_duplicates(
        subset=[
            "district_key",
            "mandal_key",
            "lat",
            "long",
        ]
    )

    return points.reset_index(
        drop=True
    )


def resolve_location(lat, lon):
    """
    Resolve GPS coordinates to the nearest
    supported district + mandal.

    If the nearest supported location is farther
    than GPS_MAX_DISTANCE_KM, the location is
    considered unsupported.
    """
    try:
        lat = float(lat)
        lon = float(lon)

    except (TypeError, ValueError):
        raise ValueError(
            "Latitude and longitude must be numeric."
        )

    if not -90 <= lat <= 90:
        raise ValueError(
            "Invalid latitude."
        )

    if not -180 <= lon <= 180:
        raise ValueError(
            "Invalid longitude."
        )

    points = get_location_points()

    if points.empty:
        return {
            "supported": False,
            "error": {
                "code": "LOCATION_DATA_UNAVAILABLE",
                "message": (
                    "No supported geographic locations "
                    "are currently available."
                ),
            },
        }

    distances = _haversine_distance_km(
        lat,
        lon,
        points["lat"].to_numpy(),
        points["long"].to_numpy(),
    )

    nearest_index = int(
        np.argmin(distances)
    )

    nearest = points.iloc[
        nearest_index
    ]

    distance_km = float(
        distances[nearest_index]
    )

    # User is outside the supported
    # groundwater assessment area.
    if distance_km > GPS_MAX_DISTANCE_KM:
        return {
            "supported": False,
            "error": {
                "code": "LOCATION_NOT_SUPPORTED",
                "message": (
                    "Your current location is outside "
                    "the supported groundwater "
                    "assessment area."
                ),
            },
        }

    return {
        "supported": True,
        "district": nearest[
            "district_key"
        ],
        "mandal": nearest[
            "mandal_key"
        ],
        "distance_km": round(
            distance_km,
            2
        ),
        "latitude": float(
            nearest["lat"]
        ),
        "longitude": float(
            nearest["long"]
        ),
        "coordinate_source": nearest.get(
            "coordinate_source",
            None
        ),
        "coordinate_quality": nearest.get(
            "coordinate_quality",
            None
        ),
    }