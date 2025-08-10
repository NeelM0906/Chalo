import os
from typing import Optional

from gtts import gTTS


class SpeechSynthesizer:
    """Online TTS using gTTS (Google Translate TTS). Generates MP3 remotely.

    Note: This sends text to Google's online service via gTTS and saves the
    returned MP3 without performing local speech synthesis.
    """

    def __init__(self, lang: str = "en", tld: str = "com", slow: bool = False) -> None:
        self.lang = lang
        self.tld = tld
        self.slow = slow

    def synthesize_to_file(self, text: str, output_path: str) -> str:
        # Enforce MP3 output to avoid local audio transcoding
        root, ext = os.path.splitext(output_path)
        if ext.lower() != ".mp3":
            output_path = f"{root}.mp3"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tts = gTTS(text=text, lang=self.lang, tld=self.tld, slow=self.slow)
        tts.save(output_path)
        return output_path

    # Backward-compatible alias used by agent
    def synthesize_to_wav(self, text: str, output_path: str) -> str:
        return self.synthesize_to_file(text, output_path)