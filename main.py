
import os
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Anime Studio AI")

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

@app.post("/generate-script")
def generate_script(data: ScriptRequest):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logging.error("GEMINI_API_KEY is missing")
        raise HTTPException(
            status_code=500,
            detail="API key is missing in Render settings."
        )

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are a professional anime explanation writer.

Write an original and engaging {data.language} script.

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
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        if not response.text:
            raise ValueError("Empty AI response")

        return {
            "success": True,
            "script": response.text
        }

    except Exception as error:
        logging.exception("GEMINI_GENERATION_ERROR")

        raise HTTPException(
            status_code=502,
            detail="AI generation failed. Check Render logs."
        )

