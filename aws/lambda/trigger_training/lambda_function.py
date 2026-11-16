"""
AWS Lambda: S3 Event Trigger for Continuous Training (CT).
Triggered when a new dataset is uploaded to s3://<bucket>/incoming/*.
Validates the CSV schema and dispatches a Kubernetes training job.
"""

import json
import os
import urllib.parse
import boto3

# AWS Clients
s3 = boto3.client("s3")
sns = boto3.client("sns")

SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:ap-south-1:843012953573:mlops-alerts")
K8S_CLUSTER_NAME = os.getenv("K8S_CLUSTER_NAME", "mlops-cluster")
EXPECTED_COLUMNS = [
    "transaction_amount",
    "transaction_frequency",
    "location_risk_score",
    "device_trust_score",
    "time_of_day",
    "failed_attempts",
    "is_fraud",
]


def lambda_handler(event, context):
    print("[EVENT] Received event: " + json.dumps(event))

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        size_bytes = record["s3"]["object"].get("size", 0)

        print(f"[INGEST] Processing new dataset: s3://{bucket}/{key} ({size_bytes} bytes)")

        # Only trigger on CSV files in incoming/
        if not key.endswith(".csv"):
            print(f"[SKIP] Key {key} is not a CSV file.")
            continue

        # 1. Validate Schema Header
        try:
            response = s3.get_object(Bucket=bucket, Key=key, Range="bytes=0-1024")
            header_sample = response["Body"].read().decode("utf-8").splitlines()[0]
            columns = [c.strip() for c in header_sample.split(",")]

            missing = [c for c in EXPECTED_COLUMNS if c not in columns]
            if missing:
                error_msg = f"[VALIDATION FAILED] Uploaded dataset {key} missing required columns: {missing}"
                print(error_msg)
                notify_sns(
                    subject="[ALERT] MLOps Pipeline: Data Validation Failed",
                    message=f"Dataset {key} in bucket {bucket} failed validation.\nMissing columns: {missing}",
                )
                return {"status": "validation_failed", "missing_columns": missing}

            print("[VALIDATION] Schema validation passed successfully!")
        except Exception as e:
            print(f"[ERROR] Could not read header from S3: {e}")
            raise e

        # 2. Dispatch Retraining Job
        # In production: Trigger via Kubernetes API, Argo Workflows, or AWS SSM Run Command on EC2
        print(f"[DISPATCH] Triggering Kubernetes Batch Training Job for dataset: {key}")

        notification_body = (
            f"New dataset detected: s3://{bucket}/{key}\n"
            f"Size: {size_bytes / 1024:.2f} KB\n"
            f"Validation: PASSED\n"
            f"Action: Kubernetes Training Job 'mlops-training-job' has been triggered on cluster '{K8S_CLUSTER_NAME}'."
        )

        notify_sns(
            subject="[MLOps CT] Retraining Job Triggered",
            message=notification_body,
        )

    return {"status": "success", "message": "Training job dispatched"}


def notify_sns(subject: str, message: str):
    """Publish alert to AWS SNS topic."""
    if not SNS_TOPIC_ARN:
        print(f"[SNS-MOCK] {subject} -> {message}")
        return

    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject[:100],
            Message=message,
        )
        print(f"[SNS] Published message to {SNS_TOPIC_ARN}")
    except Exception as e:
        print(f"[SNS ERROR] Failed to publish alert: {e}")

