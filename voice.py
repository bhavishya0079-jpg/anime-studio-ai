
import os
import base64
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from google import genai

router = APIRouter()
logger = logging.getLogger(__name__)

MODEL = "gemini-3.8-flash-tts"

AVAILABLE_VOICES = [
    "Aoede",
    "Kore",
    "Puck",
    "Charon",
    "Fenrir",
    "Leda",
    "Orus",
    "Zephyr"
]


class VoiceRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    voice: str = "Kore"
    style: str = "Natural, expressive Hindi narration"


@router.get("/voice-status")
def voice_status():
    return {
        "status": "ready",
        "model": MODEL,
        "voices": AVAILABLE_VOICES
    }


@router.post("/generate-voice")
def generate_voice(request: VoiceRequest):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing in Render."
        )

    if request.voice not in AVAILABLE_VOICES:
        raise HTTPException(
            status_code=400,
            detail="Invalid voice selected."
        )

    try:
        client = genai.Client(
            api_key=api_key,
            http_options={
                "api_version": "v1beta"
            }
        )

        interaction = client.interactions.create(
            model=MODEL,
            input=[{
                "type": "user_input",
                "content": [{
                    "type": "text",
                    "text": request.text,
                    "annotations": [{
                        "type": "speech_metadata",
                        "style": request.style
                    }]
                }]
            }],
            response_format={
                "type": "audio"
            },
            generation_config={
                "speech_config": [
                    {"voice": request.voice}
                ]
            }
        )

        if not interaction.output_audio:
            raise HTTPException(
                status_code=502,
                detail="Gemini returned no audio."
            )

        audio_data = interaction.output_audio.data

        if not audio_data:
            raise HTTPException(
                status_code=502,
                detail="Audio data is empty."
            )

        audio_bytes = base64.b64decode(audio_data)

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition":
                'attachment; filename="anime-voice.wav"'
            }
        )

    except HTTPException:
        raise

    except Exception as error:
        logger.exception("Voice generation failed")

        raise HTTPException(
            status_code=500,
            detail="Voice generation failed: " + str(error)
        )
        
