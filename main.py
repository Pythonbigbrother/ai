from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from yt_dlp import YoutubeDL
import os
import uuid

app = FastAPI()

# ✅ Allow your frontend origins
origins = [
    "https://frontend-9wkj.vercel.app",
    "https://blueberryultra.com",
    "https://www.blueberryultra.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Input model
class DownloadRequest(BaseModel):
    url: str
    format: str  # e.g. 'mp4', 'mp3'

# ✅ Download endpoint
@app.post("/download")
async def download_media(data: DownloadRequest):
    url = data.url
    fmt = data.format

    temp_id = str(uuid.uuid4())
    outtmpl = f"{temp_id}.%(ext)s"
    ydl_opts = {
        'outtmpl': outtmpl,
        'format': 'bestaudio/best' if fmt == 'mp3' else 'best',
    }

    if fmt == 'mp3':
        ydl_opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            if fmt == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'

        return FileResponse(filename, filename=os.path.basename(filename), media_type='application/octet-stream')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Root check
@app.get("/")
async def root():
    return {"message": "Downloader API is live"}
