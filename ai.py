import requests
import base64
import sys
import wave
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBNnR0YAg5Q6BTCc69lMkylugx3fduRE60")

def build_system_prompt(topic, duration, speakers_config):
    base_intro = f"""
You are an AI specializing in writing podcast scripts. Your task is to create a dialogue that feels like a lively, engaging, and humorous intellectual sparring match. The conversation must be dynamic, fast-paced, and above all, thought-provoking.
The desired podcast length is approximately {duration} minutes.

#### General Conversation Style:
The guiding style is one of sharp and amused cynicism. The speakers don't aim to belittle or dismiss; they use biting wit as a tool to expose absurdities, deconstruct conventions, and examine ideas from unexpected angles. The dialogue should be intelligent yet accessible; critical, yet driven by genuine curiosity. The goal is to make the listener smile, but more importantly, to make them think.
"""
    output_structure_template = '''
#### Exact Output Structure:

1.  English Directive:
    *   The output must begin directly with an English directive for a Text-to-Speech (TTS) model.
    *   This directive will describe only the required manner of speaking (tone, pace, style). Do not mention the episode's topic.
    *   The speaking styles for the speakers must be different and adapted for each new script.
    *   Crucially: The directive must be written as a single, continuous sentence describing the dynamic between the speakers (e.g., "[EXAMPLE_DIRECTIVE]"). It should not be broken down into a list format with separate instructions for each speaker.
    *   The directive should state that short vocal cues in parentheses, like (צוחק) or (אנחה), should be incorporated and used sparingly.
    *   The cues will be in Hebrew, without Nikkud, and include only simple, audible actions (no facial expressions or gestures).
    *   The English directive must not end with a colon (:).

2.  Hebrew Dialogue:
    *   Immediately following the English directive, the dialogue will appear.
    *   Speaker names will appear in English: [SPEAKER_TAGS].
    *   Ensure grammatically correct gender agreement throughout the dialogue (masculine/feminine forms) to maintain natural and fluent Hebrew.
    *   The entire text will be in Hebrew, without Nikkud (vocalization).
'''
    if speakers_config == "two_males":
        character_profiles = '''
#### Character Profiles:
Their interaction is the heart of the podcast. They complement and challenge each other.
*   speaker1: He possesses a captivating intellectual presence and a lively, fascinating speaking style. He uses sharp cynicism and provocative arguments to deconstruct ideas, captivating the listener.
*   speaker2: He is a natural storyteller with a calm, resonant voice. He often grounds the abstract arguments of speaker1 with historical anecdotes, real-world examples, and a touch of philosophical melancholy.
'''
        speaker_tags = '`speaker1:`, `speaker2:`'
        example_directive = 'speaker1 should adopt a thoughtfully provocative tone, while speaker2 counters with calm, story-driven insights'
    elif speakers_config == "two_females":
        character_profiles = '''
#### Character Profiles:
Their interaction is the heart of the podcast. They complement and challenge each other.
*   speaker1: She possesses a quicker, more energetic wit. She acts as a pragmatic foil, bringing discussions back to the human element with playful irony.
*   speaker2: She has a more deliberate, thoughtful delivery. She enjoys exploring the philosophical and societal implications of the topic, expanding the conversation with 'what if' scenarios and dry humor.
'''
        speaker_tags = '`speaker1:`, `speaker2:`'
        example_directive = 'speaker1 should adopt a rapid-fire, incisive style, while speaker2 responds with thoughtful, philosophical expansions'
    else:
        character_profiles = '''
#### Character Profiles:
Their interaction is the heart of the podcast. They complement and challenge each other.
*   man: He possesses a captivating intellectual presence and a lively, fascinating speaking style. His approach is analytical, but he presents it with engaging energy and personal charm. He uses sharp cynicism and provocative arguments to deconstruct ideas.
*   girl: She possesses a quicker, more energetic wit. She often acts as a pragmatic foil to his statements, bringing the discussion back down to earth with playful irony.
'''
        speaker_tags = '`man:`, `girl:`'
        example_directive = 'man should adopt a thoughtfully provocative tone, while girl counters with rapid-fire, incisive questions'
    output_structure = output_structure_template.replace('[SPEAKER_TAGS]', speaker_tags).replace('[EXAMPLE_DIRECTIVE]', example_directive)
    return f"{base_intro}\n{character_profiles}\n{output_structure}"

def generate_script(topic, duration, speakers_config):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = build_system_prompt(topic, duration, speakers_config)
    body = {
        "systemInstruction": {"parts": [{"text": prompt}]},
        "contents": [{"parts": [{"text": f"Topic: {topic}"}]}]
    }
    resp = requests.post(url, json=body)
    resp.raise_for_status()
    data = resp.json()
    script = data['candidates'][0]['content']['parts'][0]['text']
    return script

def create_wav_file(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

def generate_audio(script, speakers_config, api_key):
    if speakers_config == "two_males":
        speech_config = {
            "multiSpeakerVoiceConfig": {
                "speakerVoiceConfigs": [
                    {"speaker": "speaker1", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Sadaltager"}}},
                    {"speaker": "speaker2", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Alnilam"}}}
                ]
            }
        }
    elif speakers_config == "two_females":
        speech_config = {
            "multiSpeakerVoiceConfig": {
                "speakerVoiceConfigs": [
                    {"speaker": "speaker1", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}},
                    {"speaker": "speaker2", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Aoede"}}}
                ]
            }
        }
    else:
        speech_config = {
            "multiSpeakerVoiceConfig": {
                "speakerVoiceConfigs": [
                    {"speaker": "man", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Sadaltager"}}},
                    {"speaker": "girl", "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}
                ]
            }
        }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": script}]}],
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
        raise Exception("לא התקבל אודיו מה-API. ייתכן שיש בעיה בתסריט או במפתח.")
    b64 = audio_part['inlineData']['data']
    pcm_bytes = base64.b64decode(b64)
    return pcm_bytes

def main():
    if len(sys.argv) < 4:
        print("Usage: python podcast.py <topic> <duration> <speakers_config>")
        sys.exit(1)
    topic = sys.argv[1]
    duration = sys.argv[2]
    speakers_config = sys.argv[3]
    script_file = "podcast_script.txt"
    if os.path.exists(script_file):
        with open(script_file, "r", encoding="utf-8") as f:
            script = f.read().strip()
        if not script:
            print("קובץ התסריט קיים אך ריק, ייווצר תסריט חדש...")
            script = generate_script(topic, duration, speakers_config)
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(script)
    else:
        print("יוצר תסריט...")
        script = generate_script(topic, duration, speakers_config)
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script)
    print("התסריט:")
    print(script)
    print("יוצר שמע...")
    audio = generate_audio(script, speakers_config, GEMINI_API_KEY)
    create_wav_file("podcast.wav", audio)
    print("הקובץ podcast.wav נוצר!")

if __name__ == "__main__":
    main()
