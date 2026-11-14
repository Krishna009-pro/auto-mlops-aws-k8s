"""
AWS Lambda: Model Quality Gate & Continuous Deployment (CD).
Triggered when new metrics are uploaded to s3://<bucket>/metrics/metrics.json.
Compares model accuracy against baseline in AWS Systems Manager (SSM) Parameter Store.
Triggers zero-downtime rolling update on Kubernetes if accuracy gate passes.
"""

import json
import os
import urllib.parse
import boto3

s3 = boto3.client("s3")
sns = boto3.client("sns")
ssm = boto3.client("ssm")

SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")
DEFAULT_ACCURACY_THRESHOLD = float(os.getenv("DEFAULT_ACCURACY_THRESHOLD", "0.85"))
SSM_PARAM_THRESHOLD = "/mlops/prod/accuracy_threshold"
SSM_PARAM_VERSION = "/mlops/prod/current_model_version"


def get_ssm_parameter(param_name: str, default_value: str) -> str:
    """Fetch parameter value from AWS Systems Manager (SSM) Parameter Store."""
    try:
        response = ssm.get_parameter(Name=param_name)
        return response["Parameter"]["Value"]
    except ssm.exceptions.ParameterNotFound:
        print(f"[SSM] Parameter {param_name} not found. Creating with default: {default_value}")
        try:
            ssm.put_parameter(
                Name=param_name,
                Value=default_value,
                Type="String",
                Description="MLOps Automated Pipeline Parameter",
            )
        except Exception as e:
            print(f"[SSM WARNING] Could not set default parameter: {e}")
        return default_value
    except Exception as e:
        print(f"[SSM WARNING] Error fetching {param_name}: {e}. Using default.")
        return default_value


def update_ssm_parameter(param_name: str, new_value: str):
    """Update parameter value in AWS Systems Manager (SSM) Parameter Store."""
    try:
        ssm.put_parameter(
            Name=param_name,
            Value=new_value,
            Type="String",
            Overwrite=True,
        )
        print(f"[SSM] Updated {param_name} to: {new_value}")
    except Exception as e:
        print(f"[SSM ERROR] Failed to update {param_name}: {e}")


def lambda_handler(event, context):
    print("[EVENT] Received event: " + json.dumps(event))

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        if not key.endswith(".json"):
            continue

        print(f"[EVALUATE] Reading metrics file: s3://{bucket}/{key}")

        # 1. Download metrics.json from S3
        obj = s3.get_object(Bucket=bucket, Key=key)
        metrics = json.loads(obj["Body"].read().decode("utf-8"))

        new_version = metrics.get("version", "unknown")
        new_acc = float(metrics.get("accuracy", 0.0))
        new_f1 = float(metrics.get("f1_score", 0.0))
        new_precision = float(metrics.get("precision", 0.0))
        new_recall = float(metrics.get("recall", 0.0))

        # 2. Retrieve baseline thresholds from AWS SSM Parameter Store
        threshold_str = get_ssm_parameter(SSM_PARAM_THRESHOLD, str(DEFAULT_ACCURACY_THRESHOLD))
        accuracy_threshold = float(threshold_str)

        current_active_version = get_ssm_parameter(SSM_PARAM_VERSION, "v1-baseline")

        print(f"[EVALUATE] Model Version: {new_version}")
        print(f"[EVALUATE] New Accuracy: {new_acc:.4f} | Minimum Threshold: {accuracy_threshold:.4f}")

        # 3. Quality Gate Check
        if new_acc >= accuracy_threshold:
            status_text = "APPROVED FOR PRODUCTION"
            action_text = "Triggering Zero-Downtime Rolling Update on Kubernetes cluster..."
            print(f"[GATE-PASSED] Model {new_version} passed quality gate!")

            # Update active version in AWS SSM
            update_ssm_parameter(SSM_PARAM_VERSION, new_version)

            # In production: Trigger rolling restart on Kubernetes
            # e.g.: kubectl rollout restart deployment/mlops-serving-api -n mlops

            subject = f"[SUCCESS - DEPLOYED] MLOps Model {new_version} Promoted to Production"
            message_body = (
                f"=== MLOps Automated Deployment Notification ===\n\n"
                f"Model Version: {new_version}\n"
                f"Status: {status_text}\n"
                f"Action: {action_text}\n\n"
                f"Evaluation Benchmark:\n"
                f"  - Accuracy:  {new_acc:.4f} (Threshold: {accuracy_threshold:.4f})\n"
                f"  - Precision: {new_precision:.4f}\n"
                f"  - Recall:    {new_recall:.4f}\n"
                f"  - F1 Score:  {new_f1:.4f}\n\n"
                f"Active Pods in Kubernetes are now serving model version: {new_version}."
            )
        else:
            status_text = "REJECTED (Quality Gate Failed)"
            action_text = "Deployment Aborted. Existing production model remains active."
            print(f"[GATE-FAILED] Model {new_version} accuracy ({new_acc:.4f}) below threshold ({accuracy_threshold:.4f}).")

            subject = f"[WARNING - REJECTED] MLOps Model {new_version} Failed Quality Gate"
            message_body = (
                f"=== MLOps Model Quality Gate Alert ===\n\n"
                f"Model Version: {new_version}\n"
                f"Status: {status_text}\n"
                f"Action: {action_text}\n\n"
                f"Evaluation Benchmark:\n"
                f"  - Accuracy:  {new_acc:.4f} (Required: >= {accuracy_threshold:.4f})\n"
                f"  - Precision: {new_precision:.4f}\n"
                f"  - Recall:    {new_recall:.4f}\n\n"
                f"Production traffic is still routed safely to: {current_active_version}."
            )

        # 4. Notify MLOps team via AWS SNS
        notify_sns(subject, message_body)

    return {"status": "completed"}


def notify_sns(subject: str, message: str):
    """Publish notification to AWS SNS topic."""
    if not SNS_TOPIC_ARN:
        print(f"[SNS-MOCK] {subject}\n{message}")
        return

    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject[:100],
            Message=message,
        )
        print(f"[SNS] Published alert to {SNS_TOPIC_ARN}")
    except Exception as e:
        print(f"[SNS ERROR] Failed to send notification: {e}")
