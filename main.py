
import os
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
from voice import router as voice_router
from video import router as video_router
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Anime Studio AI")
app.include_router(voice_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ScriptRequest(BaseModel):
    anime: str = Field(min_length=1, max_length=100)
    episode: str = Field(default="Not specified", max_length=30)
    video_type: str = Field(default="Anime Explanation", max_length=40)
    language: str = Field(default="Hindi", max_length=20)
    duration: str = Field(default="3 Minutes", max_length=30)
    instructions: str = Field(default="", max_length=1000)


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Anime Studio AI Backend is running!"
    }


def is_temporary_error(error):
    message = str(error).upper()

    return any(code in message for code in [
        "503",
        "UNAVAILABLE",
        "500",
        "502",
        "504"
    ])


@app.post("/generate-script")
def generate_script(data: ScriptRequest):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing in Render settings."
        )

    primary_model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash"
    )

    fallback_model = os.getenv(
        "GEMINI_FALLBACK_MODEL",
        "gemini-3.5-flash-lite"
    )

    models = list(dict.fromkeys([
        primary_model,
        fallback_model
    ]))

    prompt = f"""
You are a professional anime explanation writer.

Create an original and engaging {data.language} script.

Anime: {data.anime}
Episode: {data.episode}
Type: {data.video_type}
Duration: {data.duration}

Instructions: {data.instructions}

Requirements:
1. Start with an exciting hook.
2. Use natural conversational language.
3. Explain events in your own words.
4. Avoid copied dialogue.
5. Do not invent episode facts.
6. Add suspense and emotion.
7. End with an engaging conclusion.
8. Make it suitable for YouTube narration.
9. Use original wording.
10. Do not reproduce copyrighted scripts.
"""

    try:
        client = genai.Client(api_key=api_key)

        for index, model in enumerate(models):

            try:
                logging.info(
                    "Generating script using model: %s",
                    model
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                script = response.text

                if not script:
                    raise ValueError("Empty AI response")

                logging.info(
                    "AI script generated successfully using %s",
                    model
                )

                return {
                    "success": True,
                    "script": script,
                    "model_used": model
                }

            except Exception as error:

                if is_temporary_error(error) and index < len(models) - 1:

                    logging.warning(
                        "Model %s is temporarily unavailable. "
                        "Trying fallback model.",
                        model
                    )

                    continue

                logging.exception(
                    "GEMINI_GENERATION_ERROR"
                )

                if is_temporary_error(error):
                    raise HTTPException(
                        status_code=503,
                        detail=(
                            "Gemini AI is temporarily busy. "
                            "Please try again after some time."
                        )
                    ) from error

                raise HTTPException(
                    status_code=502,
                    detail="AI generation failed. Check Render logs."
                ) from error

    except HTTPException:
        raise

    except Exception as error:
        logging.exception("BACKEND_ERROR")

        raise HTTPException(
            status_code=500,
            detail="Backend error. Check Render logs."
        ) from error
        
