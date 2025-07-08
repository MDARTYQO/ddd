import suno

cookie = "b6ee24df-9f7e-4bbf-a4e8-3e40faf5faed"  # הכנס כאן את העוגיה שלך

client = suno.Suno(cookie=cookie)

clips = client.songs.generate(
    "שיר שמח על קיץ וחוף ים בעברית",
    instrumental=False,
)

clip = clips[0]
print("Song ID:", clip.id)
print("Audio URL:", clip.audio_url)
print("Lyrics:", clip.metadata.get("prompt", ""))

suno.download(clip, root=".")

with open("lyrics.txt", "w", encoding="utf-8") as f:
    f.write(clip.metadata.get("prompt", ""))

print("Song and lyrics saved.")
