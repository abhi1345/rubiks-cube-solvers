import json
import os
import base64
import boto3
import urllib.request

s3 = boto3.client("s3")

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# Correct endpoint with working model
MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

def load_prompt():
    with open("prompt.txt", "r") as f:
        return f.read()

PROMPT = load_prompt()

def call_gemini(image_bytes: bytes):
    image_b64 = base64.b64encode(image_bytes).decode()

    # Build payload: image + simple prompt
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_b64
                        }
                    },
                    {"text": PROMPT}
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
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def extract_grid_from_response(response):
    text = response["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)

def validate_grid(grid):
    if len(grid) != 3:
        raise ValueError("Grid must have 3 rows")

    for row in grid:
        if len(row) != 3:
            raise ValueError("Each row must have 3 columns")
        for val in row:
            if not isinstance(val, int) or val < 0 or val > 5:
                raise ValueError(f"Invalid color value: {val}")

def lambda_handler(event, context):
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    obj = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = obj["Body"].read()

    print("Calling Gemini...")
    response = call_gemini(image_bytes)

    grid_obj = extract_grid_from_response(response)
    grid = grid_obj["grid"]

    validate_grid(grid)

    print("Parsed grid:")
    print(grid)

    return {
        "ok": True,
        "grid": grid
    }
