import os
import shutil
import subprocess
from typing import Optional

try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover
    pyttsx3 = None  # type: ignore


class SpeechSynthesizer:
    """Offline speech synthesizer using pyttsx3 if available, otherwise espeak-ng CLI."""

    def __init__(self, voice_name: Optional[str] = None, rate_wpm: int = 175, volume: float = 1.0) -> None:
        self.voice_name = voice_name
        self.rate_wpm = rate_wpm
        self.volume = max(0.0, min(1.0, volume))
        self._engine = None

        # Try initializing pyttsx3; if it fails, fall back to espeak-ng CLI
        if pyttsx3 is not None:
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", self.rate_wpm)
                engine.setProperty("volume", self.volume)
                if self.voice_name is not None:
                    self._set_pyttsx3_voice_by_name(engine, self.voice_name)
                self._engine = engine
            except Exception:
                self._engine = None

        # Ensure espeak-ng exists if we don't have a working pyttsx3 engine
        if self._engine is None and shutil.which("espeak-ng") is None:
            raise RuntimeError(
                "No TTS backend available. Install espeak-ng or ensure pyttsx3 works with eSpeak."
            )

    def _set_pyttsx3_voice_by_name(self, engine: "pyttsx3.Engine", name_substring: str) -> None:
        voices = engine.getProperty("voices")
        for v in voices:
            if name_substring.lower() in (getattr(v, "name", "") or "").lower():
                engine.setProperty("voice", v.id)
                break

    def synthesize_to_wav(self, text: str, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if self._engine is not None:
            self._engine.save_to_file(text, output_path)
            self._engine.runAndWait()
            return output_path
        return self._synthesize_with_espeak_cli(text, output_path)

    def _synthesize_with_espeak_cli(self, text: str, output_path: str) -> str:
        cmd = ["espeak-ng", "-s", str(self.rate_wpm), "-w", output_path]
        if self.voice_name:
            cmd.extend(["-v", self.voice_name])
        # Pass text as a separate argument to avoid shell quoting issues
        cmd.append(text)
        subprocess.run(cmd, check=True)
        return output_path