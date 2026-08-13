# YouTube Short Publisher

Simple pipeline for publishing a finished vertical MP4 to YouTube Shorts.

## Normal workflow

1. ChatGPT prepares `inbox/metadata.json` with the final YouTube title, description, tags, and privacy status.
2. Upload the finished video to `inbox/short.mp4` and commit it to `main`.
3. GitHub Actions automatically:
   - validates that the video is portrait and <= 3 minutes,
   - adds the fixed background music from `assets/music/Just Stay - Aakash Gandhi.mp3`,
   - preserves the original video stream without re-encoding it,
   - uploads the finished MP4 to YouTube.

## Required repository secrets

Add these under **Settings → Secrets and variables → Actions → Repository secrets**:

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

The workflow uploads as `public` by default through `inbox/metadata.json`.

## Files

- `inbox/short.mp4` — the video to publish
- `inbox/metadata.json` — title/description/tags/privacy
- `assets/music/Just Stay - Aakash Gandhi.mp3` — fixed background music
- `scripts/youtube_upload.py` — YouTube Data API uploader
- `.github/workflows/upload-short.yml` — automatic workflow
