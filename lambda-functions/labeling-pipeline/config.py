"""Configuration, AWS clients, and event helpers for the labeling pipeline."""
import os
from typing import Any, Dict

import boto3

MODEL = "gemini-2.5-flash"
PROMPT_VERSION = "v1"
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BUCKET_NAME = os.environ.get("BUCKET_NAME")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
)
# Default number of labels per scheduled run; keep here for reuse.
MAX_BACKFILL_LABELS = 500

# Shared AWS client
s3 = boto3.client("s3")


def is_s3_event(event: Dict[str, Any]) -> bool:
    """Return True if the Lambda event was triggered from S3."""
    return (
        isinstance(event, dict)
        and "Records" in event
        and len(event["Records"]) > 0
        and "s3" in event["Records"][0]
    )
