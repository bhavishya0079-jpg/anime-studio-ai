
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai

app = FastAPI(title="Anime Studio AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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
        raise HTTPException(
            status_code=500,
            detail="AI API key is not configured."
        )

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are a professional anime content scriptwriter.

Write an original and engaging {data.language} script.

Anime/Topic: {data.anime}
Episode: {data.episode}
Video Type: {data.video_type}
Duration: {data.duration}
Extra Instructions: {data.instructions}

Requirements:
1. Use natural, engaging Hindi narration.
2. Start with an interesting hook.
3. Explain events clearly in your own words.
4. Do not copy official dialogue or existing scripts.
5. Do not invent episode facts. Mention uncertainty when needed.
6. End with an engaging conclusion.
7. Format the script for voiceover.
8. Do not claim that the script guarantees copyright-free status.
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        if not response.text:
            raise HTTPException(
                status_code=502,
                detail="AI returned an empty response."
            )

        return {
            "success": True,
            "script": response.text
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI generation failed. Please try again later."
        )
      
