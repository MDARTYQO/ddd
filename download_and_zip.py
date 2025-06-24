# דרישות: pip install yt-dlp
import yt_dlp
import zipfile
import os
import sys

# קבלת כתובת הסרטון מהפרמטרים
if len(sys.argv) > 1:
    video_url = sys.argv[1]
else:
    print("יש לספק כתובת סרטון יוטיוב כפרמטר.")
    sys.exit(1)

output_filename = "video.mp4"
cookiefile = "cookies.txt" if os.path.exists("cookies.txt") else None

ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
    'outtmpl': output_filename,
    'merge_output_format': 'mp4'
}
if cookiefile:
    ydl_opts['cookiefile'] = cookiefile

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])

zip_filename = "video.zip"
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    zipf.write(output_filename)

os.remove(output_filename)
print(f"נוצר קובץ ZIP בשם: {zip_filename}")
