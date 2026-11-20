
import os
import shutil
import tempfile
import subprocess
import logging

from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import imageio_ffmpeg

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_VIDEO_SIZE = 100 * 1024 * 1024
MAX_AUDIO_SIZE = 20 * 1024 * 1024
MAX_MUSIC_SIZE = 30 * 1024 * 1024

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".ogg"}


async def save_upload(upload, destination, allowed, max_size):
    extension = Path(upload.filename or "").suffix.lower()

    if extension not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format."
        )

    total = 0

    with open(destination, "wb") as output:
        while True:
            chunk = await upload.read(1024 * 1024)

            if not chunk:
                break

            total += len(chunk)

            if total > max_size:
                raise HTTPException(
                    status_code=413,
                    detail="Uploaded file is too large."
                )

            output.write(chunk)

    if total == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )


@router.get("/video-status")
def video_status():
    return {
        "status": "ready",
        "message": "Anime Studio AI Video Editor is ready."
    }


@router.post("/render-short")
async def render_short(
    video: UploadFile = File(...),
    voice: UploadFile = File(...),
    music: UploadFile = File(None)
):
    work_dir = tempfile.mkdtemp(prefix="anime_short_")

    try:
        video_path = os.path.join(work_dir, "input_video")
        voice_path = os.path.join(work_dir, "voice_audio")
        music_path = os.path.join(work_dir, "background_music")
        output_path = os.path.join(work_dir, "anime-short.mp4")

        await save_upload(
            video,
            video_path,
            VIDEO_EXTENSIONS,
            MAX_VIDEO_SIZE
        )

        await save_upload(
            voice,
            voice_path,
            AUDIO_EXTENSIONS,
            MAX_AUDIO_SIZE
        )

        if music is not None:
            await save_upload(
                music,
                music_path,
                AUDIO_EXTENSIONS,
                MAX_MUSIC_SIZE
            )

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

        command = [
            ffmpeg,
            "-y",
            "-stream_loop", "-1",
            "-i", video_path,
            "-i", voice_path
        ]

        if music is not None:
            command.extend(["-i", music_path])

            audio_filter = (
                "[1:a]volume=1.0[voice];"
                "[2:a]volume=0.12[music];"
                "[voice][music]amix=inputs=2:"
                "duration=first:dropout_transition=2[aout]"
            )

            command.extend([
                "-filter_complex", audio_filter,
                "-map", "0:v:0",
                "-map", "[aout]"
            ])
        else:
            command.extend([
                "-map", "0:v:0",
                "-map", "1:a:0"
            ])

        command.extend([
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,setsar=1,fps=30",
            "-t", "60",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            output_path
        ])

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=240
        )

        if result.returncode != 0 or not os.path.exists(output_path):
            logger.error("FFmpeg error: %s", result.stderr[-3000:])
            raise HTTPException(
                status_code=500,
                detail="Video rendering failed. Please try another video."
            )

        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="anime-studio-short.mp4",
            background=BackgroundTask(
                shutil.rmtree,
                work_dir,
                ignore_errors=True
            )
        )

    except HTTPException:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise

    except subprocess.TimeoutExpired:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(
            status_code=504,
            detail="Video editing took too long. Try a shorter video."
        )

    except Exception:
        logger.exception("Video rendering failed")
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(
            status_code=500,
            detail="Video editor error. Please try again."
      )
      
