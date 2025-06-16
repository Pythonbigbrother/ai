from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pytube import YouTube
import instaloader
import os
import uuid

# Create FastAPI app
app = FastAPI()

# CORS Configuration
origins = [
    "https://blueberryultra.com",
    "https://www.blueberryultra.com",
    "https://frontend-9wkj.vercel.app",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory to serve downloaded files
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Request schema
class DownloadRequest(BaseModel):
    url: str
    type: str  # "video", "audio", or "playlist"

@app.post("/download")
async def download_media(request: DownloadRequest):
    url = request.url
    download_type = request.type
    try:
        # ---- YouTube download ----
        if "youtube.com" in url or "youtu.be" in url:
            yt = YouTube(url)
            filename = f"{uuid.uuid4().hex}.mp4"

            if download_type == "audio":
                stream = yt.streams.filter(only_audio=True).first()
                filename = f"{uuid.uuid4().hex}.mp3"
            elif download_type == "video":
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            elif download_type == "playlist":
                return {"success": False, "error": "Playlist support coming soon."}
            else:
                return {"success": False, "error": "Invalid download type."}

            if not stream:
                return {"success": False, "error": "Stream not found."}

            stream.download(output_path="static", filename=filename)

            return {
                "success": True,
                "download_url": f"https://ai-ai-9a7b.up.railway.app/static/{filename}"
            }

        # ---- Instagram download ----
        elif "instagram.com" in url:
            shortcode = url.strip("/").split("/")[-1]
            loader = instaloader.Instaloader(dirname_pattern="static", filename_pattern="{shortcode}")
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            loader.download_post(post, target="")

            # This assumes .mp4 or .jpg file saved
            for file in os.listdir("static"):
                if shortcode in file:
                    return {
                        "success": True,
                        "download_url": f"https://ai-ai-9a7b.up.railway.app/static/{file}"
                    }
            return {"success": False, "error": "Instagram media not found after download."}

        else:
            return {"success": False, "error": "Unsupported URL."}

    except Exception as e:
        return {"success": False, "error": str(e)}
