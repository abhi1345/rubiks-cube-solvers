import json
import os
import base64
import boto3
import urllib.request

s3 = boto3.client("s3")

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-1.5-pro-vision:generateContent"
)

def call_gemini(image_bytes):
    image_b64 = base64.b64encode(image_bytes).decode()

    payload = {
        "contents": [{
            "parts": [
                {"text": "Describe this image briefly."},
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": image_b64
                    }
                }
            ]
        }]
    }

    req = urllib.request.Request(
        f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def lambda_handler(event, context):
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    obj = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = obj["Body"].read()

    print("Calling Gemini...")
    response = call_gemini(image_bytes)

    print("Gemini raw response:")
    print(json.dumps(response, indent=2))

    return {"ok": True}