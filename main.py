from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from pytube import YouTube
import os
import uuid
import yt_dlp

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class DownloadRequest(BaseModel):
    url: str
    type: str

@app.post("/download")
async def download_video(req: DownloadRequest):
    try:
        url = req.url
        mode = req.type.lower()
        filename = f"{uuid.uuid4()}.mp4" if mode == "video" else f"{uuid.uuid4()}.mp3"
        output_path = os.path.join(DOWNLOAD_DIR, filename)

        if "instagram.com" in url or "youtu" in url:
            ydl_opts = {
                'format': 'bestaudio/best' if mode == 'audio' else 'best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }] if mode == 'audio' else []
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return JSONResponse({"success": True, "download_url": f"/file/{filename}"})
        else:
            return JSONResponse({"success": False, "error": "Unsupported platform"})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@app.get("/file/{filename}")
async def serve_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename=filename)
    return JSONResponse({"success": False, "error": "File not found"})