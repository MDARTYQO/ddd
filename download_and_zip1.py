import yt_dlp
import os
import sys

# קבלת כתובת הסרטון מהפרמטרים
if len(sys.argv) > 1:
    video_url = sys.argv[1]
else:
    print("יש לספק כתובת סרטון יוטיוב כפרמטר.")
    sys.exit(1)

cookiefile = "cookies.txt" if os.path.exists("cookies.txt") else None

# תבנית שם הקובץ: שם הסרטון + סיומת mp4
output_template = "%(title)s.%(ext)s"

def is_playlist_or_channel(url):
    return (
        "playlist" in url or
        "/channel/" in url or
        "/user/" in url or
        "/c/" in url
    )

ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
    'outtmpl': output_template,
    'merge_output_format': 'mp4',
}

if cookiefile:
    ydl_opts['cookiefile'] = cookiefile

if is_playlist_or_channel(video_url):
    ydl_opts['noplaylist'] = False
    ydl_opts['playlistend'] = 10
else:
    ydl_opts['noplaylist'] = True

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(video_url, download=True)
    if 'entries' in info:
        for entry in info['entries']:
            filename = ydl.prepare_filename(entry)
            print(f"נשמר קובץ הווידאו בשם: {filename}")
    else:
        filename = ydl.prepare_filename(info)
        print(f"נשמר קובץ הווידאו בשם: {filename}")
