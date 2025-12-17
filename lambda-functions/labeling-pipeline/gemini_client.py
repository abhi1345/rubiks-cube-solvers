"""Wrapper around the Gemini HTTP API with retry logic."""
import base64
import json
import time
import urllib.request
from typing import Any, Dict
from urllib.error import HTTPError, URLError

from config import GEMINI_API_KEY, GEMINI_URL
from prompt_loader import PROMPT


def call_gemini(image_bytes: bytes) -> Dict[str, Any]:
    image_b64 = base64.b64encode(image_bytes).decode()

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_b64,
                        }
                    },
                    {"text": PROMPT},
                ]
            }
        ]
    }

    req = urllib.request.Request(
        GEMINI_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def call_gemini_with_retry(image_bytes: bytes, max_retries: int = 3) -> Dict[str, Any]:
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            return call_gemini(image_bytes)

        except HTTPError as e:
            if 500 <= e.code < 600:
                print(f"Gemini {e.code} error, retry {attempt}/{max_retries}")
                last_error = e
            else:
                raise

        except URLError as e:
            print(f"Gemini network error, retry {attempt}/{max_retries}")
            last_error = e

        time.sleep(2 ** attempt)

    raise RuntimeError(f"Gemini failed after {max_retries} retries: {last_error}")
