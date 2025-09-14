import yt_dlp
import os
import sys

# Get video URL
if len(sys.argv) > 1:
    video_url = sys.argv[1]
else:
    print("יש לספק כתובת סרטון יוטיוב כפרמטר.")
    sys.exit(1)

cookiefile = "cookies.txt" if os.path.exists("cookies.txt") else None

# Use title-based naming; if you want a fixed name, set to "downloaded_video.%(ext)s"
output_template = "%(title)s.%(ext)s"

def is_playlist_or_channel(url: str) -> bool:
    return (
        "playlist" in url
        or "/channel/" in url
        or "/user/" in url
        or "/c/" in url
    )

ydl_opts = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
    "outtmpl": output_template,
    "merge_output_format": "mp4",
    "noprogress": True,
    "quiet": True,  # keep stdout clean
}

if cookiefile:
    ydl_opts["cookiefile"] = cookiefile

if is_playlist_or_channel(video_url):
    ydl_opts["noplaylist"] = False
    ydl_opts["playlistend"] = 10
else:
    ydl_opts["noplaylist"] = True

downloaded_paths = []

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(video_url, download=True)
    if info is None:
        print("ההורדה נכשלה.")
        sys.exit(2)

    def to_final_mp4(path: str) -> str:
        base, _ = os.path.splitext(path)
        return base + ".mp4"

    if "entries" in info and info["entries"]:
        for entry in info["entries"]:
            if not entry:
                continue
            p = ydl.prepare_filename(entry)
            final_path = to_final_mp4(p)
            downloaded_paths.append(final_path)
            print(f"FILEPATH::{final_path}")
    else:
        p = ydl.prepare_filename(info)
        final_path = to_final_mp4(p)
        downloaded_paths.append(final_path)
        print(f"FILEPATH::{final_path}")

# Optional: write list to file for debugging
try:
    with open("downloaded_files.txt", "w", encoding="utf-8") as f:
        for p in downloaded_paths:
            f.write(p + "\n")
except Exception as e:
    print(f"warn: failed to write downloaded_files.txt: {e}")

# Official GitHub Actions outputs (if available)
gout = os.environ.get("GITHUB_OUTPUT")
if gout:
    try:
        with open(gout, "a", encoding="utf-8") as f:
            # first file (handy for single video case)
            f.write(f"file={downloaded_paths[0]}\n")
            # multi-line list for playlists
            f.write("files<<EOF\n")
            for p in downloaded_paths:
                f.write(p + "\n")
            f.write("EOF\n")
    except Exception as e:
        print(f"warn: failed to write GITHUB_OUTPUT: {e}")
