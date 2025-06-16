from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pytube import YouTube
import instaloader
import os
import uuid
import traceback

app = FastAPI()

# ✅ Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://blueberryultra.com"],  # Change to your domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Download request model
class DownloadRequest(BaseModel):
    url: str
    type: str  # "video", "audio", or "playlist"

# 🔽 YouTube video/audio downloader
def download_youtube(url: str, type_: str) -> str:
    yt = YouTube(url)
    if type_ == "audio":
        stream = yt.streams.filter(only_audio=True).first()
        ext = ".mp3"
    else:
        stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
        ext = ".mp4"

    if not stream:
        raise Exception("No suitable stream found")

    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join("downloads", filename)
    os.makedirs("downloads", exist_ok=True)
    stream.download(output_path="downloads", filename=filename)
    return f"/files/{filename}"

# 🔽 Instagram downloader
def download_instagram(url: str) -> str:
    shortcode = url.strip("/").split("/")[-1]
    loader = instaloader.Instaloader(dirname_pattern="downloads")
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    loader.download_post(post, target=shortcode)
    return f"/downloads/{shortcode}"

# 🎯 Main API endpoint
@app.post("/download")
async def download(req: DownloadRequest):
    try:
        if "youtube.com" in req.url or "youtu.be" in req.url:
            file_path = download_youtube(req.url, req.type)
            public_url = f"https://ai-ai-9a7b.up.railway.app{file_path}"
            return {"success": True, "download_url": public_url}
        elif "instagram.com" in req.url:
            file_path = download_instagram(req.url)
            return {"success": True, "download_url": file_path}
        else:
            return {"success": False, "error": "Unsupported URL"}
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }

# 🔗 Serve downloaded files
from fastapi.staticfiles import StaticFiles
app.mount("/files", StaticFiles(directory="downloads"), name="files")
