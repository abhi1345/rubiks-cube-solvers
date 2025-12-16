import json
import os
import base64
import urllib.request

GEMINI_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.5-flash"

url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

def call_gemini(image_bytes):
    b64 = base64.b64encode(image_bytes).decode()

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64
                        }
                    },
                    {"text": "Describe this image."}
                ]
            }
        ]
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "x-goog-api-key": GEMINI_KEY,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())