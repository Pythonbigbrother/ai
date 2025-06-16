from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import uuid

app = FastAPI()

# CORS for your frontend
origins = [
    "https://blueberryultra.com",
    "http://localhost:3000"  # Optional for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str
    format: str  # e.g. 'mp4' or 'mp3'

@app.post("/download")
async def download_video(request: DownloadRequest):
    video_url = request.url
    video_format = request.format
    output_filename = f"{uuid.uuid4()}.%(ext)s"
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if video_format == 'mp4' else 'bestaudio',
        'outtmpl': output_filename,
        'quiet': True,
        'noplaylist': True,
    }

    if video_format == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.download([video_url])

        return {
            "success": True,
            "message": f"Download completed.",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

