from typing import Dict, List

from pydantic import BaseModel, Field


class LocationRequest(BaseModel):
    district: str = Field(
        ...,
        min_length=1,
        description="District name"
    )

    mandal: str = Field(
        ...,
        min_length=1,
        description="Mandal name"
    )


class PredictionResult(BaseModel):
    classification: str
    confidence: float = Field(
        ...,
        ge=0,
        le=1
    )
    probabilities: Dict[str, float]


class ObservationInfo(BaseModel):
    date: str | None = None
    village: str | None = None


class ModelInfo(BaseModel):
    name: str
    version: str


class PredictionResponse(BaseModel):
    location: LocationRequest
    observation: ObservationInfo
    prediction: PredictionResult
    model: ModelInfo


class KeyFactor(BaseModel):
    factor: str
    explanation: str


class ExplanationResult(BaseModel):
    summary: str
    key_factors: List[KeyFactor]
    recommendations: List[str]
    disclaimer: str


class AnalyzeResponse(BaseModel):
    location: LocationRequest
    observation: ObservationInfo
    prediction: PredictionResult
    groundwater: dict
    rainfall: dict
    explanation: ExplanationResult
    model: ModelInfo