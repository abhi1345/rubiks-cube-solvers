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

def is_s3_event(event):
    return (
        isinstance(event, dict)
        and "Records" in event
        and len(event["Records"]) > 0
        and "s3" in event["Records"][0]
    )

def process_single_image(bucket: str, key: str):
    # Skip non-images defensively
    if not key.lower().endswith(".jpg"):
        return

    label_key = (
        key.replace("dofbot/captures/", "dofbot/labels/")
           .rsplit(".", 1)[0]
        + ".json"
    )

    # Idempotency: skip if label already exists
    try:
        s3.head_object(Bucket=bucket, Key=label_key)
        print(f"Label already exists, skipping: {label_key}")
        return
    except s3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] != "404":
            raise

    obj = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = obj["Body"].read()

    response = call_gemini(image_bytes)

    text = response["candidates"][0]["content"]["parts"][0]["text"]
    grid_obj = json.loads(text)
    grid = grid_obj["grid"]

    validate_grid(grid)

    s3.put_object(
        Bucket=bucket,
        Key=label_key,
        Body=json.dumps(
            {
                "grid": grid,
                "model": MODEL,
            }
        ).encode(),
        ContentType="application/json",
    )

    print(f"Wrote label: {label_key}")

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

def backfill_unlabeled_images(bucket: str, max_images: int = 50):
    paginator = s3.get_paginator("list_objects_v2")
    processed = 0

    for page in paginator.paginate(
        Bucket=bucket,
        Prefix="dofbot/captures/"
    ):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            process_single_image(bucket, key)
            processed += 1

            if processed >= max_images:
                print("Backfill cap reached, stopping")
                return

def lambda_handler(event, context):
    if is_s3_event(event):
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"S3 trigger for {key}")
        process_single_image(bucket, key)

    else:
        bucket = os.environ["BUCKET_NAME"]
        print("Running hourly backfill")
        backfill_unlabeled_images(bucket)

    return {"ok": True}
