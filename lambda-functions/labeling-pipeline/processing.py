"""High-level labeling workflows."""
import json
from datetime import datetime
from typing import Any, Dict, List

from config import MODEL, PROMPT_VERSION, s3
from gemini_client import call_gemini_with_retry


def extract_grid_from_response(response: Dict[str, Any]) -> Dict[str, Any]:
    try:
        text = response["candidates"][0]["content"]["parts"][0]["text"]

        if not text or not text.strip():
            raise ValueError("Empty Gemini response")

        # Log raw output for troubleshooting unexpected formats
        print("Raw Gemini output:")
        print(repr(text))

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in Gemini output")

        json_str = text[start : end + 1]
        return json.loads(json_str)

    except Exception as e:  # noqa: BLE001 - surface parsing failure context
        raise ValueError(f"Failed to parse Gemini response: {e}") from e


def validate_grid(grid: List[List[int]]) -> None:
    if len(grid) != 3:
        raise ValueError("Grid must have 3 rows")

    for row in grid:
        if len(row) != 3:
            raise ValueError("Each row must have 3 columns")
        for val in row:
            if not isinstance(val, int) or val < 0 or val > 5:
                raise ValueError(f"Invalid color value: {val}")


def process_single_image(bucket: str, key: str) -> bool:
    try:
        if not key.lower().endswith(".jpg"):
            return False

        label_key = (
            key.replace("dofbot/captures/", "dofbot/labels/").rsplit(".", 1)[0] + ".json"
        )

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

    except Exception as e:  # noqa: BLE001 - log and continue processing
        print(f"Failed to label {key}: {e}")
        return False


def backfill_unlabeled_images(bucket: str, max_labels: int = 5) -> None:
    paginator = s3.get_paginator("list_objects_v2")
    labeled = 0

    for page in paginator.paginate(Bucket=bucket, Prefix="dofbot/captures/"):
        for obj in page.get("Contents", []):
            if labeled >= max_labels:
                print("Hourly label cap reached, stopping")
                return

            key = obj["Key"]
            if process_single_image(bucket, key):
                labeled += 1
