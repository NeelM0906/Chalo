from typing import Dict

from .ai_engine import AIEngine
from .tts_engine import SpeechSynthesizer


class LocalGuideAgent:
    def __init__(self, ai_engine: AIEngine, speech_synthesizer: SpeechSynthesizer) -> None:
        self.ai_engine = ai_engine
        self.speech_synthesizer = speech_synthesizer

    def handle_query(self, user_query: str, output_audio_path: str) -> Dict[str, str]:
        engine_response = self.ai_engine.query(user_query)
        ai_text = str(engine_response.get("text", "")).strip()

        if not ai_text:
            ai_text = (
                "I don't have enough information to provide a recommendation right now."
                " Please try asking in a different way."
            )

        # Prefer synthesize_to_file; fall back to synthesize_to_wav for compatibility
        if hasattr(self.speech_synthesizer, "synthesize_to_file"):
            audio_path = self.speech_synthesizer.synthesize_to_file(ai_text, output_audio_path)
        else:
            audio_path = self.speech_synthesizer.synthesize_to_wav(ai_text, output_audio_path)
        return {
            "recommendation_text": ai_text,
            "audio_path": audio_path,
        }