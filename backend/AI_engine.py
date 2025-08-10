"""
Yelp AI Chat v2 client.

- Reads API key from environment variable `YELP_API_KEY`
- Provides a function `ask_yelp_ai` for programmatic use
- Includes a simple CLI for ad-hoc testing

Usage (CLI):
    python backend/AI_engine.py --query "What's a good vegan pizza place near me?" \
        --lat 40.7128 --lon -74.0060 --locale en_US

Requires: requests, python-dotenv (optional for loading .env)
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

YELP_AI_CHAT_URL = "https://api.yelp.com/ai/chat/v2"
DEFAULT_OUTPUT_FILENAME = "AI_search_results.json"
DEFAULT_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), DEFAULT_OUTPUT_FILENAME)


@dataclass
class UserContext:
    # All fields optional per Yelp AI docs; lat/lon are optional
    locale: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        # Include only provided values
        data: Dict[str, Any] = {}
        if self.locale is not None:
            data["locale"] = self.locale
        if self.latitude is not None:
            data["latitude"] = self.latitude
        if self.longitude is not None:
            data["longitude"] = self.longitude
        return data


class YelpAIError(Exception):
    pass


def _get_api_key() -> str:
    """Fetch Yelp API key from env, raising if missing."""
    load_dotenv()  # no-op if no .env
    api_key = "dnUhOwLs5n21ToEMEYQ8TDeraOF-8X8iMWouWoGzHYZpIDpe_ZOxPUUxOh2Hykp-u9MRHPbM5n3gGW0qBnK_Jq0i0qa17VpHifx-Jz9xbXL7VPnYXB6ss-NMhyiYaHYx"
    if not api_key:
        raise YelpAIError(
            "YELP_API_KEY is not set. Add it to your environment or backend/.env"
        )
    return api_key


def ask_yelp_ai(query: str, user_context: UserContext, timeout_seconds: int = 20) -> Dict[str, Any]:
    """
    Send a chat request to Yelp AI Chat v2.

    Returns parsed JSON dict on success; raises YelpAIError on failures.
    """
    api_key = _get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "query": query,
        "user_context": user_context.to_dict(),
    }

    try:
        response = requests.post(
            YELP_AI_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=timeout_seconds,
        )
    except requests.RequestException as exc:
        raise YelpAIError(f"Network error calling Yelp AI: {exc}") from exc

    if response.status_code >= 400:
        # Try to include response body for easier debugging
        body: str
        try:
            body = response.text
        except Exception:
            body = "<unreadable body>"
        raise YelpAIError(
            f"Yelp AI returned HTTP {response.status_code}: {body}"
        )

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise YelpAIError("Failed to parse Yelp AI JSON response") from exc

    return data


def save_json_to_file(data: Dict[str, Any], file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _get_nested(dct: Dict[str, Any], *keys: str) -> Optional[Any]:
    current: Any = dct
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def _extract_chat_id(raw: Dict[str, Any]) -> Optional[str]:
    candidates = [
        raw.get("chat_id"),
        raw.get("id"),
        _get_nested(raw, "message", "id"),
        _get_nested(raw, "conversation", "id"),
        _get_nested(raw, "meta", "chat_id"),
    ]
    for val in candidates:
        if isinstance(val, str) and val:
            return val
    return None


def _extract_text(raw: Dict[str, Any]) -> Optional[str]:
    candidates = [
        raw.get("text"),
        _get_nested(raw, "response", "text"),
        _get_nested(raw, "output", "text"),
        _get_nested(raw, "message", "text"),
    ]
    for val in candidates:
        if isinstance(val, str) and val:
            return val

    # Try messages array formats
    messages = raw.get("messages")
    if isinstance(messages, list) and messages:
        last = messages[-1]
        if isinstance(last, dict):
            text = last.get("text") or last.get("content")
            if isinstance(text, str) and text:
                return text
    return None


def _iter_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for v in value.values():
            yield from _iter_dicts(v)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_dicts(item)


def _looks_like_business(obj: Dict[str, Any]) -> bool:
    if not isinstance(obj, dict):
        return False
    has_id = isinstance(obj.get("id"), str)
    has_name = isinstance(obj.get("name"), str)
    has_any_business_hint = any(
        key in obj for key in ["url", "location", "coordinates", "review_count", "price", "rating"]
    )
    return has_id and has_name and has_any_business_hint


def _collect_businesses(raw: Dict[str, Any]) -> list[Dict[str, Any]]:
    # Priority: top-level common keys
    candidates_lists: list[Any] = []
    for key_path in [
        ("businesses",),
        ("results", "businesses"),
        ("data", "businesses"),
        ("response", "businesses"),
        ("entities",),
    ]:
        container = _get_nested(raw, *key_path) if len(key_path) > 1 else raw.get(key_path[0])
        if isinstance(container, list):
            candidates_lists.append(container)

    businesses: list[Dict[str, Any]] = []
    seen_ids: set[str] = set()

    # From candidate lists
    for lst in candidates_lists:
        for item in lst:
            if isinstance(item, dict) and _looks_like_business(item):
                bid = item.get("id")
                if isinstance(bid, str) and bid not in seen_ids:
                    businesses.append(item)
                    seen_ids.add(bid)

    # Fallback: recursive scan for business-like dicts
    if not businesses:
        for obj in _iter_dicts(raw):
            if _looks_like_business(obj):
                bid = obj.get("id")
                if isinstance(bid, str) and bid not in seen_ids:
                    businesses.append(obj)
                    seen_ids.add(bid)

    return businesses


def _normalize_location(loc: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(loc, dict):
        return {}
    display_address = loc.get("display_address")
    formatted_address = None
    if isinstance(display_address, list):
        formatted_address = ", ".join([str(part) for part in display_address if part])
    elif isinstance(loc.get("formatted_address"), str):
        formatted_address = loc.get("formatted_address")

    return {
        "address1": loc.get("address1"),
        "address2": loc.get("address2"),
        "city": loc.get("city"),
        "zip_code": loc.get("zip_code"),
        "state": loc.get("state"),
        "country": loc.get("country"),
        "formatted_address": formatted_address,
    }


def _transform_business(b: Dict[str, Any]) -> Dict[str, Any]:
    coordinates = b.get("coordinates") if isinstance(b.get("coordinates"), dict) else {}
    about = b.get("about_this_business") if isinstance(b.get("about_this_business"), dict) else {}
    photos: Optional[list] = None
    phoos: Optional[list[str]] = None  # Explicit list of original_url links
    # Try multiple common shapes for photos
    if isinstance(b.get("photos"), list):
        raw_list = b.get("photos")
        # Collect any string URLs directly
        str_urls = [p for p in raw_list if isinstance(p, str)]
        photos = str_urls or None
        # Collect original_url from dict entries
        extracted: list[str] = []
        for item in raw_list:
            if isinstance(item, dict):
                # direct key
                url = item.get("original_url")
                # sometimes nested under link or image objects
                if not url and isinstance(item.get("link"), dict):
                    url = item.get("link", {}).get("original_url")
                if not url and isinstance(item.get("image"), dict):
                    url = item.get("image", {}).get("original_url")
                if isinstance(url, str):
                    extracted.append(url)
        if extracted:
            phoos = extracted
    elif isinstance(b.get("images"), list):
        photos = [p for p in b.get("images") if isinstance(p, str)] or None
    elif isinstance(b.get("photo_urls"), list):
        photos = [p for p in b.get("photo_urls") if isinstance(p, str)] or None
    # Yelp AI: contextual_info.photos is a list of {original_url}
    if not phoos:
        contextual_info = b.get("contextual_info")
        if isinstance(contextual_info, dict):
            ci_photos = contextual_info.get("photos")
            if isinstance(ci_photos, list):
                extracted: list[str] = []
                for item in ci_photos:
                    if isinstance(item, dict):
                        url = item.get("original_url")
                        if isinstance(url, str):
                            extracted.append(url)
                if extracted:
                    phoos = extracted

    # Try common image fields
    image_url = (
        b.get("image_url")
        or b.get("imageUrl")
        or b.get("cover_photo")
        or b.get("coverPhoto")
        or b.get("main_image")
        or b.get("mainImage")
        or b.get("photo")
        or b.get("photo_url")
        or b.get("thumbnail_url")
    )
    # Prefer phoos (high quality originals) for primary image
    if not image_url and phoos and len(phoos) > 0:
        image_url = phoos[0]
    elif not image_url and photos and len(photos) > 0:
        image_url = photos[0]

    return {
        "id": b.get("id"),
        "alias": b.get("alias"),
        "name": b.get("name"),
        "url": b.get("url"),
        "image_url": image_url,
        "photos": photos,
        "phoos": phoos,
        "location": _normalize_location(b.get("location")),
        "coordinates": {
            "lat": coordinates.get("latitude"),
            "lng": coordinates.get("longitude"),
        },
        "review_count": b.get("review_count"),
        "price": b.get("price"),
        "rating": b.get("rating"),
        "AboutThisBizBio": about.get("bio") or b.get("about_this_biz_bio") or b.get("about_bio"),
        "AboutThisBizHistory": about.get("history") or b.get("about_this_biz_history") or b.get("about_history"),
        "AboutThisBizSpecialties": about.get("specialties") or b.get("about_this_biz_specialties") or b.get("about_specialties"),
        "AboutThisBizYearEstablished": about.get("year_established") or b.get("about_this_biz_year_established") or b.get("year_established"),
    }


def transform_yelp_ai_response(raw: Dict[str, Any]) -> Dict[str, Any]:
    chat_id = _extract_chat_id(raw)
    text = _extract_text(raw)
    businesses_raw = _collect_businesses(raw)
    businesses = [_transform_business(b) for b in businesses_raw]

    return {
        "chat_id": chat_id,
        "text": text,
        "businesses": businesses,
    }


def _parse_cli_args(argv: list[str]) -> Optional[Dict[str, Any]]:
    import argparse

    parser = argparse.ArgumentParser(description="Query Yelp AI Chat v2")
    parser.add_argument("--query", required=True, help="User query text")
    parser.add_argument("--lat", type=float, required=False, help="Latitude (optional)")
    parser.add_argument("--lon", type=float, required=False, help="Longitude (optional)")
    parser.add_argument("--locale", required=False, default="en_US", help="Locale, e.g., en_US (optional)")
    parser.add_argument("--timeout", type=int, default=20, help="Timeout seconds")
    parser.add_argument(
        "--out",
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output JSON file path (default: {DEFAULT_OUTPUT_PATH})",
    )

    if len(argv) == 0:
        parser.print_help()
        return None

    args = parser.parse_args(argv)

    return {
        "query": args.query,
        "context": UserContext(
            locale=args.locale,
            latitude=args.lat,
            longitude=args.lon,
        ),
        "timeout": args.timeout,
        "out_path": args.out,
    }


def main(argv: list[str]) -> int:
    parsed = _parse_cli_args(argv)
    if not parsed:
        return 2

    try:
        result = ask_yelp_ai(parsed["query"], parsed["context"], parsed["timeout"])
    except YelpAIError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    transformed = transform_yelp_ai_response(result)
    print(json.dumps(transformed, indent=2, ensure_ascii=False))
    try:
        save_json_to_file(transformed, parsed["out_path"])
    except OSError as exc:
        print(f"Warning: failed to write output JSON to {parsed['out_path']}: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
