import os
import suno

cookie = os.environ.get("SUNO_COOKIE")
if not cookie:
    raise Exception("SUNO_COOKIE environment variable not set")

client = suno.Suno(cookie=cookie)

# יצירת שיר חדש
clips = client.songs.generate(
    "שיר שמח על קיץ וחוף ים בעברית",
    instrumental=False,
)

clip = clips[0]
print("Song ID:", clip.id)
print("Audio URL:", clip.audio_url)
print("Lyrics:", clip.metadata.get("prompt", ""))

# הורדת השיר
suno.download(clip, root=".")

# שמירת המילים
with open("lyrics.txt", "w", encoding="utf-8") as f:
    f.write(clip.metadata.get("prompt", ""))

print("Song and lyrics saved.")
