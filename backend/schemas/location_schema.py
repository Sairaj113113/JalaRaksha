from pydantic import BaseModel, Field
from typing import Optional


class LocationRequest(BaseModel):
    district: str = Field(
        ...,
        min_length=1,
        description="District name",
    )

    mandal: str = Field(
        ...,
        min_length=1,
        description="Mandal name",
    )


class LocationResponse(BaseModel):
    district: str
    mandal: str
    distance_km: Optional[float] = None


class GPSLocationResponse(BaseModel):
    district: str
    mandal: str
    distance_km: float