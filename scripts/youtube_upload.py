import json
import os
import subprocess
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_metadata(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    tags = data.get("tags", ["Shorts"])
    privacy = str(data.get("privacyStatus", "public")).strip().lower()

    if not title:
        raise ValueError("metadata.json: title is required")
    if len(title) > 100:
        raise ValueError(f"YouTube title is too long: {len(title)} chars")
    if privacy not in {"private", "unlisted", "public"}:
        raise ValueError(f"Invalid privacyStatus: {privacy}")
    if not isinstance(tags, list):
        raise ValueError("metadata.json: tags must be a list")

    if "#shorts" not in title.lower() and "#shorts" not in description.lower():
        description = (description + "\n\n#Shorts").strip()

    return {
        "title": title,
        "description": description,
        "tags": [str(x) for x in tags],
        "privacyStatus": privacy,
    }


def inspect_video(path: Path) -> None:
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,codec_name,pix_fmt:format=duration",
                "-of", "json", str(path),
            ],
            text=True,
        )
    )
    stream = probe["streams"][0]
    width = int(stream["width"])
    height = int(stream["height"])
    duration = float(probe["format"]["duration"])
    codec = stream.get("codec_name", "unknown")
    pix_fmt = stream.get("pix_fmt", "unknown")

    print(f"Video: {width}x{height}, {duration:.3f}s, codec={codec}, pix_fmt={pix_fmt}")
    if width >= height:
        raise RuntimeError(f"Video is not portrait: {width}x{height}")
    if duration > 180.0:
        raise RuntimeError(f"Video is longer than 3 minutes: {duration:.3f}s")


def build_credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=require_env("YOUTUBE_REFRESH_TOKEN"),
        token_uri=TOKEN_URI,
        client_id=require_env("YOUTUBE_CLIENT_ID"),
        client_secret=require_env("YOUTUBE_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def upload(video_path: Path, metadata: dict) -> str:
    youtube = build("youtube", "v3", credentials=build_credentials(), cache_discovery=False)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata["tags"],
                "categoryId": "25",
            },
            "status": {
                "privacyStatus": metadata["privacyStatus"],
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            chunksize=8 * 1024 * 1024,
            resumable=True,
        ),
        notifySubscribers=False,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status is not None:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"YouTube upload successful: {video_id}")
    print(f"https://www.youtube.com/shorts/{video_id}")
    return video_id


def main() -> None:
    video_path = Path(os.environ.get("VIDEO_PATH", "output/short_with_music.mp4"))
    metadata_path = Path(os.environ.get("METADATA_PATH", "inbox/metadata.json"))

    if not video_path.is_file():
        raise FileNotFoundError(video_path)
    if not metadata_path.is_file():
        raise FileNotFoundError(metadata_path)

    inspect_video(video_path)
    metadata = load_metadata(metadata_path)
    print(f"Title: {metadata['title']}")
    print(f"Privacy: {metadata['privacyStatus']}")
    upload(video_path, metadata)


if __name__ == "__main__":
    main()
