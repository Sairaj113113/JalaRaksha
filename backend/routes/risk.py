from fastapi import APIRouter, HTTPException

from backend.schemas.risk_schema import (
    AnalyzeResponse,
    LocationRequest,
    ModelInfo,
    ObservationInfo,
    PredictionResponse,
    PredictionResult,
)
from backend.services.location_service import (
    get_latest_observation,
)
from backend.services.current_condition_service import (
    build_current_observation,
)
from backend.services.risk_service import (
    predict_observation,
)


router = APIRouter(
    prefix="",
    tags=["Risk Analysis"],
)


MODEL_INFO = ModelInfo(
    name="Jala Raksha Random Forest",
    version="1.0.0",
)


def build_observation_info(observation):
    """
    Convert the observation into the API observation structure.
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


def get_prediction(district, mandal):
    """
    Existing prediction pipeline.

    Uses the latest real groundwater observation.
    Kept for the /predict endpoint.
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

    return observation, prediction


def get_current_prediction(district, mandal):
    """
    Current Jala Raksha analysis pipeline.

    1. Use historical groundwater data.
    2. Estimate the current month's groundwater level.
    3. Build a current-month feature row.
    4. Classify the estimated current condition.
    """
    observation = build_current_observation(
        district,
        mandal,
    )

    if observation is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "INSUFFICIENT_HISTORICAL_DATA",
                "message": (
                    "Insufficient historical groundwater "
                    "data is available to estimate the "
                    "current condition for this location."
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
                    "Unable to generate current "
                    "groundwater risk prediction."
                ),
            },
        ) from exc

    return observation, prediction


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(request: LocationRequest):
    """
    Generate a groundwater classification
    using the latest real observation.
    """
    observation, prediction = get_prediction(
        request.district,
        request.mandal,
    )

    return PredictionResponse(
        location=request,
        observation=build_observation_info(
            observation
        ),
        prediction=PredictionResult(
            **prediction
        ),
        model=MODEL_INFO,
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
def analyze(request: LocationRequest):
    """
    Main Jala Raksha analysis endpoint.

    Uses historical groundwater and rainfall data
    to estimate the current month's groundwater
    condition and classify the estimated risk.
    """

    observation, prediction = get_current_prediction(
        request.district,
        request.mandal,
    )

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

    groundwater = {
        "value": (
            float(groundwater_value)
            if pd_not_null(groundwater_value)
            else None
        ),
        "unit": "m",
    }

    rainfall = {
        "monthly_rainfall_mm": (
            float(rainfall_value)
            if pd_not_null(rainfall_value)
            else None
        ),
        "rainfall_days": (
            int(rainfall_days)
            if pd_not_null(rainfall_days)
            else None
        ),
        "available": (
            bool(rainfall_available)
            if pd_not_null(rainfall_available)
            else False
        ),
        "confidence": (
            str(rainfall_confidence)
            if pd_not_null(rainfall_confidence)
            else None
        ),
        "station_distance_km": (
            float(station_distance)
            if pd_not_null(station_distance)
            else None
        ),
    }

    target_date = observation.get(
        "date"
    )

    if target_date is not None:
        target_date = str(
            target_date
        )

    last_real_date = observation.get(
        "last_real_observation_date"
    )

    explanation = {
        "summary": (
            f"The model estimates the current "
            f"groundwater level at "
            f"{groundwater_value:.3f} m and "
            f"classifies the current condition as "
            f"{prediction['classification']}."
        ),
        "key_factors": [
            {
                "factor": "Estimated groundwater level",
                "explanation": (
                    "The current groundwater level "
                    "is a model estimate derived from "
                    "historical groundwater observations."
                ),
            },
            {
                "factor": "Historical groundwater trend",
                "explanation": (
                    "Historical groundwater behavior "
                    "was used to estimate the current "
                    "month's groundwater condition."
                ),
            },
            {
                "factor": "Rainfall conditions",
                "explanation": (
                    "Historical rainfall behavior for "
                    "the current calendar month was "
                    "used to construct the current "
                    "risk-model input."
                ),
            },
        ],
        "recommendations": [
            "Monitor groundwater levels regularly.",
            "Track rainfall trends over time.",
            "Use the prediction as decision-support information.",
        ],
        "disclaimer": (
            "This is an AI-generated estimate based "
            "on historical groundwater and rainfall "
            "data. It is not a direct measurement of "
            "current groundwater conditions."
        ),
        "estimated": True,
        "target_date": target_date,
        "last_real_observation_date": (
            last_real_date
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


def pd_not_null(value):
    """
    Safely check whether a value is not null,
    including pandas/NumPy values.
    """
    if value is None:
        return False

    try:
        return not bool(
            __import__("pandas").isna(value)
        )
    except (TypeError, ValueError):
        return True