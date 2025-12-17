import json
import os
import base64
import boto3
import urllib.request
import time
from datetime import datetime
from urllib.error import HTTPError, URLError

# --------------------
# AWS clients
# --------------------
s3 = boto3.client("s3")

# --------------------
# Environment variables
# --------------------
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BUCKET_NAME = os.environ.get("BUCKET_NAME")

# --------------------
# Gemini config
# --------------------
MODEL = "gemma-3-12b"
PROMPT_VERSION = "v1"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# --------------------
# Helpers
# --------------------
def is_s3_event(event):
    return (
        isinstance(event, dict)
        and "Records" in event
        and len(event["Records"]) > 0
        and "s3" in event["Records"][0]
    )


def load_prompt():
    with open("prompt.txt", "r") as f:
        return f.read()


PROMPT = load_prompt()

# --------------------
# Gemini call + retry
# --------------------
def call_gemini(image_bytes: bytes):
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


def call_gemini_with_retry(image_bytes: bytes, max_retries: int = 3):
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

# --------------------
# Parsing + validation
# --------------------
def extract_grid_from_response(response):
    try:
        text = response["candidates"][0]["content"]["parts"][0]["text"]

        if not text or not text.strip():
            raise ValueError("Empty Gemini response")

        # Log raw output once for debugging
        print("Raw Gemini output:")
        print(repr(text))

        # Extract JSON object from text
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in Gemini output")

        json_str = text[start:end + 1]
        return json.loads(json_str)

    except Exception as e:
        raise ValueError(f"Failed to parse Gemini response: {e}")


def validate_grid(grid):
    if len(grid) != 3:
        raise ValueError("Grid must have 3 rows")

    for row in grid:
        if len(row) != 3:
            raise ValueError("Each row must have 3 columns")
        for val in row:
            if not isinstance(val, int) or val < 0 or val > 5:
                raise ValueError(f"Invalid color value: {val}")

# --------------------
# Core labeling logic
# --------------------
def process_single_image(bucket: str, key: str) -> bool:
    try:
        if not key.lower().endswith(".jpg"):
            return False

        label_key = (
            key.replace("dofbot/captures/", "dofbot/labels/")
            .rsplit(".", 1)[0]
            + ".json"
        )

        # Idempotency check
        try:
            s3.head_object(Bucket=bucket, Key=label_key)
            print(f"Label already exists, skipping: {label_key}")
            return False
        except s3.exceptions.ClientError as e:
            if e.response["Error"]["Code"] != "404":
                raise

        obj = s3.get_object(Bucket=bucket, Key=key)
        image_bytes = obj["Body"].read()

        response = call_gemini_with_retry(image_bytes)
        grid_obj = extract_grid_from_response(response)

        grid = grid_obj["grid"]
        validate_grid(grid)

        s3.put_object(
            Bucket=bucket,
            Key=label_key,
            Body=json.dumps(
                {
                    "grid": grid,
                    "model": MODEL,
                    "prompt_version": PROMPT_VERSION,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            ).encode(),
            ContentType="application/json",
        )

        print(f"Wrote label: {label_key}")
        return True

    except Exception as e:
        print(f"Failed to label {key}: {e}")
        return False

# --------------------
# Hourly backfill (rate-limited)
# --------------------
def backfill_unlabeled_images(bucket: str, max_labels: int = 5):
    paginator = s3.get_paginator("list_objects_v2")
    labeled = 0

    for page in paginator.paginate(
        Bucket=bucket,
        Prefix="dofbot/captures/",
    ):
        for obj in page.get("Contents", []):
            if labeled >= max_labels:
                print("Hourly label cap reached, stopping")
                return

            key = obj["Key"]
            if process_single_image(bucket, key):
                labeled += 1

# --------------------
# Lambda entrypoint
# --------------------
def lambda_handler(event, context):
    if is_s3_event(event):
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"S3 trigger for {key}")
        process_single_image(bucket, key)

    else:
        print("Running scheduled backfill (max 5 labels)")
        backfill_unlabeled_images(BUCKET_NAME, max_labels=5)

    return {"ok": True}