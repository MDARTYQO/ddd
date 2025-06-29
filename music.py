import asyncio
from google import genai
from google.genai import types
import wave
import os

GOOGLE_API_KEY = "AIzaSyB_YKFGkAxGAMBVT2plc2jEGhPcFl6IiIw"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
client = genai.Client(http_options={'api_version': 'v1alpha'})

async def main():
    async def receive_audio(session):
        wf = wave.open("bouncy_track.wav", "wb")
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        try:
            async for message in session.receive():
                print("התקבלה הודעה מהשרת")
                if message.server_content.audio_chunks:
                    audio_data = message.server_content.audio_chunks[0].data
                    wf.writeframes(audio_data)
        finally:
            wf.close()
            print("הקובץ bouncy_track.wav נוצר!")

    async with (
        client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
        asyncio.TaskGroup() as tg,
    ):
        # Set up task to receive server messages.
        tg.create_task(receive_audio(session))

        # Send initial prompts and config
        await session.set_weighted_prompts(
            prompts=[
                types.WeightedPrompt(text='energetic dance, bouncy, electronic, uplifting, festival, party', weight=1.0),
            ]
        )
        await session.set_music_generation_config(
            config=types.LiveMusicGenerationConfig(bpm=128, temperature=1.0)
        )

        # Start streaming music
        await session.play()
        await asyncio.sleep(20)  # זמן יצירה (שניות), אפשר להגדיל/להקטין

if __name__ == "__main__":
    asyncio.run(main())
