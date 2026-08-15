from fastapi import APIRouter, HTTPException

from backend.schemas.risk_schema import (
    AnalyzeResponse,
    LocationRequest,
    PredictionResult,
    ObservationInfo,
    ModelInfo,
)
from backend.services.location_service import (
    get_latest_observation,
)
from backend.services.risk_service import (
    predict_observation,
)
from backend.services.explanation_service import (
    generate_explanation,
)


router = APIRouter(
    prefix="",
    tags=["Explanation"],
)


MODEL_INFO = ModelInfo(
    name="Jala Raksha Random Forest",
    version="1.0.0",
)


def build_observation_info(observation):
    """
    Convert the raw observation into the API observation structure.
    """
    date_value = observation.get("date")

    if date_value is not None:
        date_value = str(date_value)

    village_value = observation.get("village")

    if village_value is not None:
        village_value = str(village_value)

    return ObservationInfo(
        date=date_value,
        village=village_value,
    )


@router.post(
    "/explain",
    response_model=AnalyzeResponse,
)
def explain(request: LocationRequest):
    """
    Generate an AI explanation for the latest
    groundwater prediction of a location.

    The same latest observation used by the
    prediction pipeline is passed to the LLM.
    """

    observation = get_latest_observation(
        request.district,
        request.mandal,
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

    try:
        prediction = predict_observation(
            observation
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "MODEL_ERROR",
                "message": (
                    "Unable to generate groundwater prediction."
                ),
            },
        ) from exc

    try:
        explanation = generate_explanation(
            district=request.district,
            mandal=request.mandal,
            observation=observation,
            prediction=prediction,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "EXPLANATION_SERVICE_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc

    groundwater_value = observation.get(
        "value"
    )

    rainfall_value = observation.get(
        "monthly_rainfall_mm_model"
    )

    rainfall_days = observation.get(
        "rainfall_days"
    )

    rainfall_available = observation.get(
        "rainfall_available"
    )

    rainfall_confidence = observation.get(
        "rainfall_confidence"
    )

    station_distance = observation.get(
        "station_distance_km"
    )

    import pandas as pd

    groundwater = {
        "value": (
            float(groundwater_value)
            if groundwater_value is not None
            and not pd.isna(groundwater_value)
            else None
        ),
        "unit": "m",
    }

    rainfall = {
        "monthly_rainfall_mm": (
            float(rainfall_value)
            if rainfall_value is not None
            and not pd.isna(rainfall_value)
            else None
        ),
        "rainfall_days": (
            int(rainfall_days)
            if rainfall_days is not None
            and not pd.isna(rainfall_days)
            else None
        ),
        "available": (
            bool(rainfall_available)
            if rainfall_available is not None
            and not pd.isna(rainfall_available)
            else False
        ),
        "confidence": (
            str(rainfall_confidence)
            if rainfall_confidence is not None
            and not pd.isna(rainfall_confidence)
            else None
        ),
        "station_distance_km": (
            float(station_distance)
            if station_distance is not None
            and not pd.isna(station_distance)
            else None
        ),
    }

    return AnalyzeResponse(
        location=request,
        observation=build_observation_info(
            observation
        ),
        prediction=PredictionResult(
            **prediction
        ),
        groundwater=groundwater,
        rainfall=rainfall,
        explanation=explanation,
        model=MODEL_INFO,
    )