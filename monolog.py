import requests
import base64
import sys
import wave
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBNnR0YAg5Q6BTCc69lMkylugx3fduRE60")

def build_system_prompt(topic, duration, famous_style=None):
    base_intro = f"""
You are an AI specializing in writing monologues for radio and podcasts. Your task is to create a monologue that feels like a sharp, witty, and slightly cynical commentary, in the style of Amit Segal, a well-known Israeli journalist.
The monologue should be dynamic, intelligent, and delivered with a news-like, confident, and slightly amused tone, as if addressing a large radio audience.
The desired monologue length is approximately {duration} minutes.

#### Speaker Style:
The speaker should imitate the speaking style, humor, and delivery of Amit Segal: clear, articulate, fast-paced, with subtle sarcasm and a touch of self-awareness. The voice should sound like a professional Israeli news anchor.

#### Exact Output Structure:
* The output should be a single, continuous monologue in Hebrew (without Nikkud), as if Amit Segal is speaking directly to the audience.
* The monologue must mention the event "סנטוחה" by name, and explain why it is simply not possible to hold such an event.
* The monologue must refer to Baruch Shoshan by name, and explain (with humor and wit) that he is a very boring person, and it is unreasonable for him to expect an exciting event when he himself is so boring.
* The text should be clever, slightly biting, and entertaining, but not offensive.
* Do not include any speaker names or dialogue format.
"""
    if famous_style and famous_style.strip():
        base_intro += f"\nThe monologue should especially resemble the style of {famous_style}.\n"
    return base_intro

def generate_monologue(topic, duration, famous_style=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = build_system_prompt(topic, duration, famous_style)
    body = {
        "systemInstruction": {"parts": [{"text": prompt}]},
        "contents": [{"parts": [{"text": f"Topic: {topic}"}]}]
    }
    resp = requests.post(url, json=body)
    resp.raise_for_status()
    data = resp.json()
    monologue = data['candidates'][0]['content']['parts'][0]['text']
    return monologue

def create_wav_file(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

def generate_audio(text, api_key):
    # Use Avri - the closest Israeli male news voice in Gemini
    speech_config = {
        "voiceConfig": {
            "prebuiltVoiceConfig": {
                "voiceName": "Avri"
            }
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": speech_config
        }
    }
    resp = requests.post(url, json=body)
    resp.raise_for_status()
    data = resp.json()
    parts = data['candidates'][0]['content']['parts']
    audio_part = next((p for p in parts if 'inlineData' in p), None)
    if not audio_part:
        raise Exception("לא התקבל אודיו מה-API. ייתכן שיש בעיה בטקסט או במפתח.")
    b64 = audio_part['inlineData']['data']
    pcm_bytes = base64.b64decode(b64)
    return pcm_bytes

def main():
    topic = "למה אי אפשר לעשות סנטוחה, במיוחד כשברוך שושן כל כך משעמם"
    duration = 2  # דקות
    famous_style = "עמית סגל"
    monologue_file = "monologue.txt"

    # יצירת מונולוג או טעינה מקובץ קיים
    if os.path.exists(monologue_file):
        with open(monologue_file, "r", encoding="utf-8") as f:
            monologue = f.read().strip()
        if not monologue:
            print("קובץ המונולוג קיים אך ריק, ייווצר מונולוג חדש...")
            monologue = generate_monologue(topic, duration, famous_style)
            with open(monologue_file, "w", encoding="utf-8") as f:
                f.write(monologue)
    else:
        print("יוצר מונולוג...")
        monologue = generate_monologue(topic, duration, famous_style)
        with open(monologue_file, "w", encoding="utf-8") as f:
            f.write(monologue)

    print("המונולוג:")
    print(monologue)
    print("יוצר שמע...")
    audio = generate_audio(monologue, GEMINI_API_KEY)
    create_wav_file("podcast.wav", audio)
    print("הקובץ podcast.wav נוצר!")

if __name__ == "__main__":
    main()
