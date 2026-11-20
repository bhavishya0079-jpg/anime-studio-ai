
import os
import base64

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from google import genai

router = APIRouter()

class VoiceRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    voice: str = "Aoede"

@router.post("/generate-voice")
def generate_voice(request: VoiceRequest):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is missing."
        )

    try:
        client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"}
        )

        result = client.interactions.create(
            model="gemini-3.8-flash-tts",
            input=[{
                "type": "user_input",
                "content": [{
                    "type": "text",
                    "text": request.text
                }]
            }],
            response_format={"type": "audio"},
            generation_config={
                "speech_config": [
                    {"voice": request.voice}
                ]
            }
        )

        if not result.output_audio or not result.output_audio.data:
            raise HTTPException(
                status_code=500,
                detail="Audio was not generated."
            )

        audio = base64.b64decode(
            result.output_audio.data
        )

        return Response(
            content=audio,
            media_type="audio/wav",
            headers={
                "Content-Disposition":
                'attachment; filename="anime-voice.wav"'
            }
        )

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
        
