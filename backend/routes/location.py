from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from backend.services.location_service import (
    get_locations,
    get_latest_observation,
    resolve_location,
)


router = APIRouter(
    prefix="",
    tags=["Location"],
)


def make_json_safe(value):
    """
    Convert pandas/NumPy values into JSON-safe Python values.
    NaN and NaT become None.
    """
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def make_observation_json_safe(observation):
    """
    Convert the complete observation into JSON-safe data.
    """
    return {
        key: make_json_safe(value)
        for key, value in observation.items()
    }


@router.get("/locations")
def locations():
    """
    Return all supported districts and their mandals.
    """
    return {
        "locations": get_locations()
    }


@router.get("/location/{district}/{mandal}")
def location(
    district: str,
    mandal: str,
):
    """
    Return the latest groundwater observation
    for a district + mandal.
    """
    observation = get_latest_observation(
        district,
        mandal,
    )

    if observation is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "LOCATION_NOT_FOUND",
                "message": (
                    "No groundwater observation found "
                    "for the requested district and mandal."
                ),
            },
        )

    safe_observation = make_observation_json_safe(
        observation
    )

    return {
        "district": safe_observation.get(
            "district_key"
        ),
        "mandal": safe_observation.get(
            "mandal_key"
        ),
        "observation": safe_observation,
    }


@router.get("/location/nearest")
def nearest_location(
    lat: float = Query(
        ...,
        description="GPS latitude",
        ge=-90,
        le=90,
    ),
    lon: float = Query(
        ...,
        description="GPS longitude",
        ge=-180,
        le=180,
    ),
):
    """
    Resolve GPS coordinates to the nearest
    supported district + mandal.
    """
    try:
        result = resolve_location(
            lat,
            lon,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_COORDINATES",
                "message": str(exc),
            },
        ) from exc

    if not result.get("supported", False):
        error = result.get(
            "error",
            {
                "code": "LOCATION_NOT_SUPPORTED",
                "message": (
                    "Your current location is outside "
                    "the supported groundwater "
                    "assessment area."
                ),
            },
        )

        raise HTTPException(
            status_code=404,
            detail=error,
        )

    return {
        "district": result["district"],
        "mandal": result["mandal"],
        "distance_km": result["distance_km"],
    }