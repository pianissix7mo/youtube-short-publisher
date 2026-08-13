# YouTube Short Publisher

Simple pipeline for publishing a finished vertical MP4 to YouTube Shorts without committing video files into Git history.

## Normal workflow

1. ChatGPT prepares `inbox/metadata.json` with the final YouTube title, description, tags, and privacy status.
2. Open **Releases → Draft a new release**.
3. Create a new temporary tag targeting `main` (for example `short-20260812-2130`).
4. Attach exactly one finished `.mp4` file to the Release.
5. Publish the Release.
6. GitHub Actions automatically:
   - downloads the MP4 Release asset,
   - validates that the video is portrait and <= 3 minutes,
   - discards any audio already present in the uploaded MP4,
   - adds only `assets/music/background.mp3`,
   - preserves the original video stream without re-encoding it,
   - uploads the finished MP4 to YouTube,
   - after a successful YouTube upload, deletes the temporary Release and its tag.

The MP4 is stored as a Release asset rather than committed to `main`, so normal repository history does not accumulate each uploaded video.

## Required repository secrets

Add these under **Settings → Secrets and variables → Actions → Repository secrets**:

- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REFRESH_TOKEN`

## Files

- `inbox/metadata.json` — title/description/tags/privacy; defaults to `public` but placeholder title/description intentionally block accidental uploads
- `assets/music/background.mp3` — fixed background music; replace this file with another file of the same name to change music
- `scripts/youtube_upload.py` — YouTube Data API uploader
- `.github/workflows/upload-short.yml` — Release-triggered automatic workflow
