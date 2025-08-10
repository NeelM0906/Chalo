#!/usr/bin/env python3
"""
Minimal CLI to test Yelp AI Chat v2 per provided docs.

- Reads API key from env YELP_API_KEY; if missing, falls back to backend.AI_engine._get_api_key()
- POST https://api.yelp.com/ai/chat/v2 with query and optional user_context
- Prints AI text and extracts business details: name, price, rating, coordinates, photos, top review
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import requests


YELP_AI_CHAT_URL = "https://api.yelp.com/ai/chat/v2"


def _get_api_key() -> str:
    key = os.getenv("YELP_API_KEY")
    if key:
        return key
    # Fallback to project helper if available
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from AI_engine import _get_api_key as _helper_get_api_key  # type: ignore

        return _helper_get_api_key()
    except Exception:
        raise RuntimeError(
            "YELP_API_KEY is not set and fallback helper was not available."
        )


def post_yelp_ai(
    query: str,
    locale: Optional[str] = "en_US",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    api_key = _get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {"query": query}
    user_context: Dict[str, Any] = {}
    if locale:
        user_context["locale"] = locale
    if latitude is not None:
        user_context["latitude"] = latitude
    if longitude is not None:
        user_context["longitude"] = longitude
    if user_context:
        payload["user_context"] = user_context

    resp = requests.post(YELP_AI_CHAT_URL, headers=headers, json=payload, timeout=timeout_seconds)
    if resp.status_code >= 400:
        raise RuntimeError(f"Yelp AI HTTP {resp.status_code}: {resp.text[:500]}")
    try:
        return resp.json()
    except Exception as exc:
        raise RuntimeError("Failed to parse Yelp AI JSON response") from exc


def _collect_businesses(obj: Any) -> List[Dict[str, Any]]:
    found: List[Dict[str, Any]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            # Common path in docs: entities -> [{ businesses: [...] }]
            if "businesses" in value and isinstance(value["businesses"], list):
                for item in value["businesses"]:
                    if isinstance(item, dict):
                        found.append(item)
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(obj)
    return found


def _extract_first(value: Any, *path: str) -> Optional[Any]:
    cur = value
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
        if cur is None:
            return None
    return cur


def _extract_business_view(b: Dict[str, Any]) -> Dict[str, Any]:
    loc = b.get("location") if isinstance(b.get("location"), dict) else {}
    coords = b.get("coordinates") if isinstance(b.get("coordinates"), dict) else {}
    ctx = b.get("contextual_info") if isinstance(b.get("contextual_info"), dict) else {}
    photos = ctx.get("photos") if isinstance(ctx.get("photos"), list) else []

    # Try to pick a concise review snippet: contextual_info.review_snippet or summaries.short
    review_snippet = None
    if isinstance(ctx.get("review_snippet"), str):
        review_snippet = ctx.get("review_snippet")
    else:
        summaries = b.get("summaries") if isinstance(b.get("summaries"), dict) else {}
        if isinstance(summaries.get("short"), str):
            review_snippet = summaries.get("short")

    # Prefer contextual_info.photos.original_url list if present
    extracted_photo_urls: List[str] = []
    for p in photos:
        if isinstance(p, dict) and isinstance(p.get("original_url"), str):
            extracted_photo_urls.append(p["original_url"]) 

    return {
        "id": b.get("id"),
        "alias": b.get("alias"),
        "name": b.get("name"),
        "url": b.get("url"),
        "formatted_address": loc.get("formatted_address"),
        "coordinates": {
            "lat": coords.get("latitude"),
            "lng": coords.get("longitude"),
        },
        "review_count": b.get("review_count"),
        "price": b.get("price"),
        "rating": b.get("rating"),
        "photos": extracted_photo_urls,
        "review_snippet": review_snippet,
    }


def _print_summary(resp: Dict[str, Any], limit: int = 5) -> None:
    text = _extract_first(resp, "response", "text") or resp.get("text")
    if text:
        print("\nAI Text:\n" + text + "\n")
    else:
        print("\nAI Text: <none>\n")

    businesses = _collect_businesses(resp)
    print(f"Found {len(businesses)} businesses\n")

    for i, b in enumerate(businesses[:limit], 1):
        v = _extract_business_view(b)
        print(f"{i}. {v['name']} ({v['rating']}⭐{(' · ' + v['price']) if v['price'] else ''})")
        if v["formatted_address"]:
            print(f"   {v['formatted_address']}")
        coords = v["coordinates"]
        if coords.get("lat") is not None and coords.get("lng") is not None:
            print(f"   ({coords['lat']}, {coords['lng']})")
        if v["photos"]:
            print(f"   photos: {len(v['photos'])} (e.g. {v['photos'][0]})")
        if v["review_snippet"]:
            print(f"   snippet: {v['review_snippet']}")
        if v["url"]:
            print(f"   url: {v['url']}")
        print()


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Test Yelp AI Chat v2")
    parser.add_argument("--query", required=True, help="User query text")
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    parser.add_argument("--locale", default="en_US", help="Locale, e.g., en_US")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout seconds")
    parser.add_argument("--out", help="Write raw JSON to this path")
    parser.add_argument("--print-raw", action="store_true", help="Also print raw JSON")

    args = parser.parse_args(argv)

    try:
        resp = post_yelp_ai(
            query=args.query,
            locale=args.locale,
            latitude=args.lat,
            longitude=args.lon,
            timeout_seconds=args.timeout,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.out:
        try:
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(resp, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            print(f"Warning: failed to write output JSON: {exc}", file=sys.stderr)

    if args.print_raw:
        print(json.dumps(resp, indent=2, ensure_ascii=False))

    _print_summary(resp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


