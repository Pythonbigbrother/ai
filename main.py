from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import yt_dlp
import io

app = FastAPI()

# Allow all origins for development (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str
    format: str = "mp4"

@app.post("/download")
async def download_video(req: DownloadRequest):
    video_url = req.url
    video_format = req.format

    try:
        buffer = io.BytesIO()

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': '-',  # Stream to stdout
            'quiet': True,
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'logtostderr': False,
            'retries': 3,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': video_format
            }],
            'stdout': buffer,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            ydl.download([video_url])

        buffer.seek(0)
        filename = f"{info['title']}.{video_format}"
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }

        return StreamingResponse(buffer, media_type="video/mp4", headers=headers)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
