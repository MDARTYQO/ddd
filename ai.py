import requests
import json
import base64
import sys

GEMINI_API_KEY = "AIzaSyBXphJJz9ygt1Jorl15H82HmSgiSyTk7AM"

def build_system_prompt(topic, duration, speakers_config):
    base_intro = f"""
אתה מחולל תסריטי פודקאסטים בעברית. הנושא: {topic}
אורך משוער: {duration} דקות.
סגנון: ציני, שנון, ביקורתי אך סקרן.
"""
    if speakers_config == "male_female":
        speaker_tags = "man:, girl:"
        example_directive = "man should adopt a thoughtfully provocative tone, while girl counters with rapid-fire, incisive questions"
    elif speakers_config == "two_males":
        speaker_tags = "speaker1:, speaker2:"
        example_directive = "speaker1 should adopt a thoughtfully provocative tone, while speaker2 counters with calm, story-driven insights"
    elif speakers_config == "two_females":
        speaker_tags = "speaker1:, speaker2:"
        example_directive = "speaker1 should adopt a rapid-fire, incisive style, while speaker2 responds with thoughtful, philosophical expansions"
    else:
        speaker_tags = "man:, girl:"
        example_directive = "man should adopt a thoughtfully provocative tone, while girl counters with rapid-fire, incisive questions"

    output_structure = f"""
1. English Directive:
   * The output must begin directly with an English directive for a Text-to-Speech (TTS) model.
   * This directive will describe only the required manner of speaking (tone, pace, style). Do not mention the episode's topic.
   * The speaking styles for the speakers must be different and adapted for each new script.
   * Crucially: The directive must be written as a single, continuous sentence describing the dynamic between the speakers (e.g., "{example_directive}"). It should not be broken down into a list format with separate instructions for each speaker.
   * The directive should state that short vocal cues in parentheses, like (צוחק) or (אנחה), should be incorporated and used sparingly.
   * The cues will be in Hebrew, without Nikkud, and include only simple, audible actions (no facial expressions or gestures).
   * The English directive must not end with a colon (:).

2. Hebrew Dialogue:
   * Immediately following the English directive, the dialogue will appear.
   * Speaker names will appear in English: {speaker_tags}
   * Ensure grammatically correct gender agreement throughout the dialogue (masculine/feminine forms) to maintain natural and fluent Hebrew.
   * The entire text will be in Hebrew, without Nikkud (vocalization).
"""
    return base_intro + output_structure

def generate_script(topic, duration, speakers_config):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = build_system_prompt(topic, duration, speakers_config)
    user_input = f"כתוב תסריט פודקאסט בנושא: {topic}"
    body = {
        "contents": [
            {"role": "system", "parts": [{"text": prompt}]},
            {"role": "user", "parts": [{"text": user_input}]}
        ]
    }
    resp = requests.post(url, json=body)
    resp.raise_for_status()
    data = resp.json()
    script = data['candidates'][0]['content']['parts'][0]['text']
    return script

def generate_audio(script):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-tts:generateContent?key={GEMINI_API_KEY}"
    body = {
        "contents": [
            {"role": "user", "parts": [{"text": script}]}
        ]
    }
    resp = requests.post(url, json=body)
    resp.raise_for_status()
    data = resp.json()
    audio_b64 = data['candidates'][0]['content']['parts'][0]['inlineData']['data']
    audio_bytes = base64.b64decode(audio_b64)
    return audio_bytes

def main():
    if len(sys.argv) < 4:
        print("Usage: python podcast_generator.py <topic> <duration> <speakers_config>")
        sys.exit(1)
    topic = sys.argv[1]
    duration = sys.argv[2]
    speakers_config = sys.argv[3]
    print("יוצר תסריט...")
    script = generate_script(topic, duration, speakers_config)
    print("התסריט נוצר:\n")
    print(script)
    with open("podcast_script.txt", "w", encoding="utf-8") as f:
        f.write(script)
    print("יוצר שמע...")
    audio = generate_audio(script)
    with open("podcast.wav", "wb") as f:
        f.write(audio)
    print("הקובץ podcast.wav נוצר!")

if __name__ == "__main__":
    main()
