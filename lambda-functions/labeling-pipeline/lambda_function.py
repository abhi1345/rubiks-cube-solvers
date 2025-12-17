"""Lambda entrypoint for the labeling pipeline."""
from config import BUCKET_NAME, MAX_BACKFILL_LABELS, is_s3_event
from processing import backfill_unlabeled_images, process_single_image


def lambda_handler(event, _context):
    if is_s3_event(event):
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print(f"S3 trigger for {key}")
        process_single_image(bucket, key)

    else:
        print(f"Running scheduled backfill (max {MAX_BACKFILL_LABELS} labels)")
        backfill_unlabeled_images(BUCKET_NAME, max_labels=MAX_BACKFILL_LABELS)

    print("Finished running labeling pipeline lambda function.")

    return {"ok": True}
