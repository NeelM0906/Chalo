import argparse
import os
from datetime import datetime

from app.ai_engine import AIEngine
from app.tts_engine import SpeechSynthesizer
from app.agent import LocalGuideAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local Guide Speech Agent (online TTS)")
    parser.add_argument("--query", required=True, help="User query to guide the recommendation")
    parser.add_argument(
        "--ai-json",
        default="/workspace/data/ai_engine_sample.json",
        help="Path to a JSON file containing AI_engine output with a 'text' field",
    )
    parser.add_argument(
        "--out",
        default="/workspace/output/recommendation.mp3",
        help="Output MP3 file path for synthesized speech (audio generated online)",
    )
    parser.add_argument(
        "--lang",
        default="en",
        help="Language code for gTTS (e.g., en, en-GB, es, fr)",
    )
    parser.add_argument(
        "--tld",
        default="com",
        help="Top-level domain for gTTS (e.g., com, co.uk). Can affect voice accent.",
    )
    parser.add_argument(
        "--slow",
        action="store_true",
        help="Use slower speech speed in gTTS",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Ensure unique default filename if user didn't override and file exists
    out_path = args.out
    if out_path == "/workspace/output/recommendation.mp3" and os.path.exists(out_path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"/workspace/output/recommendation_{ts}.mp3"

    ai_engine = AIEngine(source_json_path=args.ai_json)
    tts = SpeechSynthesizer(lang=args.lang, tld=args.tld, slow=args.slow)
    agent = LocalGuideAgent(ai_engine=ai_engine, speech_synthesizer=tts)

    result = agent.handle_query(args.query, out_path)

    print("Recommendation:\n")
    print(result["recommendation_text"])

    print("\nAudio saved to:", result["audio_path"])


if __name__ == "__main__":
    main()