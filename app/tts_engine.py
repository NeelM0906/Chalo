import os
import subprocess
from typing import Optional


class SpeechSynthesizer:
    """Text-to-speech using Hugging Face SpeechT5 locally. Falls back to espeak-ng CLI if HF stack unavailable."""

    def __init__(self, voice_name: Optional[str] = None, rate_wpm: int = 175, volume: float = 1.0) -> None:
        self.voice_name = voice_name
        self.rate_wpm = rate_wpm
        self.volume = max(0.0, min(1.0, volume))

        # Lazily initialized HF artifacts
        self._hf_ready = False
        self._processor = None
        self._model = None
        self._vocoder = None
        self._speaker_embeddings = None

    def _init_hf(self) -> None:
        if self._hf_ready:
            return
        try:
            import torch
            from transformers import (
                SpeechT5ForTextToSpeech,
                SpeechT5HifiGan,
                SpeechT5Processor,
            )
            from datasets import load_dataset

            self._processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
            self._model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
            self._vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

            # Speaker embedding: use CMU Arctic xvectors (public, on HF hub)
            xvectors = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
            # Pick an arbitrary, but good-sounding speaker embedding
            speaker_embedding = xvectors[7306]["xvector"]
            if not hasattr(torch, "tensor"):
                raise RuntimeError("PyTorch not available for HF TTS")
            import torch as _torch

            self._speaker_embeddings = _torch.tensor(speaker_embedding).unsqueeze(0)
            self._hf_ready = True
        except Exception as exc:  # pragma: no cover
            # Mark as not ready; caller can attempt fallback
            self._hf_ready = False
            self._processor = None
            self._model = None
            self._vocoder = None
            self._speaker_embeddings = None
            self._hf_error = exc  # for optional inspection

    def synthesize_to_wav(self, text: str, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Try HF path first
        try:
            return self._synthesize_with_hf(text, output_path)
        except Exception:
            # Fall back to espeak-ng CLI if available
            return self._synthesize_with_espeak_cli(text, output_path)

    def _synthesize_with_hf(self, text: str, output_path: str) -> str:
        self._init_hf()
        if not self._hf_ready or self._processor is None or self._model is None or self._vocoder is None:
            raise RuntimeError("HF TTS not ready")

        import numpy as np
        import scipy.io.wavfile as wavfile
        import torch

        inputs = self._processor(text=text, return_tensors="pt")
        with torch.no_grad():
            speech = self._model.generate_speech(
                inputs["input_ids"],
                self._speaker_embeddings,
                vocoder=self._vocoder,
            )
        # speech is a torch.FloatTensor [num_samples]
        audio = speech.cpu().numpy()
        # Normalize to int16 range, 16kHz sample rate per SpeechT5 default
        audio_int16 = np.int16(audio / max(1e-8, np.max(np.abs(audio))) * 32767)
        wavfile.write(output_path, 16000, audio_int16)
        return output_path

    def _synthesize_with_espeak_cli(self, text: str, output_path: str) -> str:
        # Fallback only; user requested HF, but this ensures some audio is produced if HF stack missing
        cmd = ["espeak-ng", "-s", str(self.rate_wpm), "-w", output_path]
        if self.voice_name:
            cmd.extend(["-v", self.voice_name])
        cmd.append(text)
        subprocess.run(cmd, check=True)
        return output_path