from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from backend.services.voice_service import generate_speech

router = APIRouter(prefix="/voice", tags=["Voice"])


class VoiceRequest(BaseModel):
    text: str


@router.post("/speak")
def speak(request: VoiceRequest):
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty",
        )

    try:
        audio = generate_speech(request.text)

        return Response(
            content=audio,
            media_type="audio/mpeg",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Voice generation failed: {exc}",
        )