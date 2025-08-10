import json
import os
from typing import Any, Dict, Optional


class AIEngine:
    """Simple AI engine client that returns a dict with a 'text' attribute.

    In a real integration, replace the file-loading logic with an API call.
    """

    def __init__(self, source_json_path: Optional[str] = None) -> None:
        self.source_json_path = source_json_path

    def query(self, user_query: str) -> Dict[str, Any]:
        """Return a response dict. Must include a 'text' field.

        If `source_json_path` is provided and exists, this function loads the
        JSON and returns it. Otherwise, returns a fallback demo response.
        """
        if self.source_json_path and os.path.exists(self.source_json_path):
            with open(self.source_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Ensure we always return a dict with at least a 'text' field
            if isinstance(data, dict) and "text" in data:
                return data

        # Fallback demo content leveraging the user query for minimal personalization
        return {
            "text": (
                f"Here is a tailored local guide recommendation based on your query '"
                f"{user_query}':\n\n"
                "Start your exploration at the central market just before lunchtime."
                " Grab a local street snack, then stroll to the old town quarter to"
                " enjoy the architecture and small artisan shops. Around golden hour,"
                " head to the riverfront viewpoint for a relaxing sunset. Finish with"
                " a cozy dinner at a family-run bistro nearby."
            )
        }