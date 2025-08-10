import json
import os
import time
from typing import Optional

import requests


class SpeechSynthesizer:
    """Text-to-speech via Hugging Face Inference API (no on-device synthesis).

    Default model: espnet/kan-bayashi-ljspeech-vits (English female voice)
    """

    def __init__(
        self,
        model_id: str = "espnet/kan-bayashi-ljspeech-vits",
        api_token: Optional[str] = None,
        timeout_seconds: float = 60.0,
        max_retries: int = 6,
        retry_delay_seconds: float = 5.0,
    ) -> None:
        self.model_id = model_id
        # Allow env var fallback
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    def synthesize_to_wav(self, text: str, output_path: str) -> str:
        root, ext = os.path.splitext(output_path)
        if ext.lower() != ".wav":
            output_path = f"{root}.wav"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        audio_bytes = self._call_hf_inference(text)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return output_path

    def _call_hf_inference(self, text: str) -> bytes:
        if not text or not text.strip():
            raise ValueError("text must be a non-empty string")

        url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        headers = {"Accept": "audio/wav"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        payload = {"inputs": text}

        # Retry on 503 (model loading) and certain transient issues
        last_err = None
        for _ in range(self.max_retries):
            try:
                resp = requests.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=self.timeout_seconds,
                )
                # 200 OK with audio content
                if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("audio/"):
                    return resp.content

                # 503: model loading - backoff and retry
                if resp.status_code == 503:
                    time.sleep(self.retry_delay_seconds)
                    continue

                # JSON error payloads
                ctype = resp.headers.get("content-type", "")
                if "application/json" in ctype:
                    try:
                        err = resp.json()
                    except Exception:
                        err = {"error": resp.text}
                else:
                    err = {"error": resp.text, "status": resp.status_code}

                # If unauthorized/no token
                if resp.status_code in (401, 403):
                    raise RuntimeError(
                        "Hugging Face Inference API authorization failed. Set HUGGINGFACE_API_TOKEN or pass --hf-token."
                    )
                last_err = RuntimeError(f"HF inference failed: {err}")
            except requests.RequestException as exc:
                last_err = exc
            time.sleep(self.retry_delay_seconds)

        if last_err is not None:
            raise last_err
        raise RuntimeError("HF inference failed after retries without specific error")