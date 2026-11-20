
import os
import io
import wave

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

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
            detail="Gemini API key is not configured."
        )

    try:
        client = genai.Client(api_key=api_key)

        result = client.models.generate_content(
            model="gemini-3.8-flash-tts",
            contents=request.text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=request.voice
                        )
                    )
                )
            )
        )

        for part in result.parts:
            if part.inline_data:
                audio_data = part.inline_data.data

                output = io.BytesIO()
                with wave.open(output, "wb") as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(24000)
                    wav.writeframes(audio_data)

                return Response(
                    content=output.getvalue(),
                    media_type="audio/wav",
                    headers={
                        "Content-Disposition":
                        'attachment; filename="anime-voice.wav"'
                    }
                )

        raise HTTPException(
            status_code=500,
            detail="No audio was generated."
        )

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
      
