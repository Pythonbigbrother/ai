from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import yt_dlp
import io

app = FastAPI()

# CORS setup: allow your frontend domain here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-9wkj.vercel.app"],  # Replace with your actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/download")
async def download_video(request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        format_type = data.get("format", "mp4")

        if not url:
            return JSONResponse(status_code=400, content={"error": "URL is required"})

        buffer = io.BytesIO()

        # Options for yt-dlp
        ydl_opts = {
            "format": "bestaudio/best" if format_type == "mp3" else "bestvideo+bestaudio/best",
            "outtmpl": "-",
            "quiet": True,
            "noplaylist": True,
            "prefer_ffmpeg": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }] if format_type == "mp3" else [],
        }

        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
        
        # Actually perform the download into the buffer
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            ext = 'mp3' if format_type == 'mp3' else 'mp4'
            filename = f"{title}.{ext}"

            ydl.download([url])
            stream = open(filename, "rb")

            return StreamingResponse(
                stream,
                media_type="audio/mpeg" if format_type == "mp3" else "video/mp4",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )

        return download()

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
