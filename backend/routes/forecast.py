from fastapi import APIRouter, HTTPException

from backend.services.forecast_service import (
    forecast_location,
)


router = APIRouter(
    prefix="",
    tags=["Forecast"],
)


@router.post("/forecast")
def forecast(
    request: dict,
):
    """
    Generate a groundwater forecast for a
    district + mandal.
    """

    district = request.get("district")
    mandal = request.get("mandal")
    periods = request.get(
        "months",
        6,
    )

    if not district or not mandal:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_REQUEST",
                "message": (
                    "district and mandal are required."
                ),
            },
        )

    try:
        periods = int(periods)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_FORECAST_MONTHS",
                "message": (
                    "months must be a valid integer."
                ),
            },
        )

    if periods < 1 or periods > 12:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_FORECAST_MONTHS",
                "message": (
                    "months must be between 1 and 12."
                ),
            },
        )

    try:
        result = forecast_location(
            district=district,
            mandal=mandal,
            periods=periods,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_FORECAST_REQUEST",
                "message": str(exc),
            },
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "FORECAST_ERROR",
                "message": (
                    "Unable to generate groundwater forecast."
                ),
            },
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "LOCATION_NOT_FOUND",
                "message": (
                    "No historical groundwater data "
                    "found for the requested district "
                    "and mandal."
                ),
            },
        )

    return result