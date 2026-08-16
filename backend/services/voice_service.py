import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

_api_key = os.getenv("ELEVENLABS_API_KEY")

if not _api_key:
    raise RuntimeError("ELEVENLABS_API_KEY is not configured")

client = ElevenLabs(api_key=_api_key)


def generate_speech(text: str) -> bytes:
    audio = client.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        text=text,
        model_id="eleven_v3",
        output_format="mp3_44100_128",
    )

    if isinstance(audio, bytes):
        return audio

    return b"".join(audio)


