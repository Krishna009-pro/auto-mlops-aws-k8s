"""
MLOps Automated Model Training Pipeline.
Trains a fraud classification model, computes metrics, and uploads artifacts to S3 / local storage.
"""

import os
import json
import argparse
from datetime import datetime
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

FEATURE_COLUMNS = [
    "transaction_amount",
    "transaction_frequency",
    "location_risk_score",
    "device_trust_score",
    "time_of_day",
    "failed_attempts",
]
TARGET_COLUMN = "is_fraud"


def load_dataset(data_path: str, s3_bucket: str = None) -> pd.DataFrame:
    """Load dataset from local filesystem or AWS S3."""
    if data_path.startswith("s3://"):
        import boto3
        import urllib.parse

        parsed = urllib.parse.urlparse(data_path)
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")

        print(f"[TRAIN] Downloading dataset from s3://{bucket}/{key}...")
        s3 = boto3.client("s3")
        local_tmp = "/tmp/downloaded_data.csv" if os.name != "nt" else "downloaded_data.csv"
        s3.download_file(bucket, key, local_tmp)
        return pd.read_csv(local_tmp)
    elif s3_bucket and not os.path.exists(data_path):
        import boto3

        print(f"[TRAIN] Fetching {data_path} from S3 bucket: {s3_bucket}...")
        s3 = boto3.client("s3")
        local_tmp = "/tmp/downloaded_data.csv" if os.name != "nt" else "downloaded_data.csv"
        s3.download_file(s3_bucket, data_path, local_tmp)
        return pd.read_csv(local_tmp)
    else:
        print(f"[TRAIN] Loading dataset from local path: {data_path}")
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data path not found: {data_path}")
        return pd.read_csv(data_path)


def train_model(
    df: pd.DataFrame,
    version: str = "v1",
    model_dir: str = "artifacts/models",
    metrics_dir: str = "artifacts/metrics",
    s3_bucket: str = None,
) -> dict:
    """Trains fraud detection pipeline and saves serialized model & metrics."""
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(metrics_dir, exist_ok=True)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    print(f"[TRAIN] Dataset size: {len(df)} rows. Features: {FEATURE_COLUMNS}")
    print(f"[TRAIN] Target distribution:\n{y.value_counts()}")

    # Stratified 80/20 split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Scikit-Learn Pipeline: Scaler + Classifier
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=100,
                    max_depth=6,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    print("[TRAIN] Fitting Random Forest model...")
    pipeline.fit(X_train, y_train)

    # Predictions & Probabilities
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    # Compute evaluation metrics
    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_prob))

    metrics = {
        "version": version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "features": FEATURE_COLUMNS,
    }

    print(f"[TRAIN] Model Training Complete!")
    print(f"[TRAIN] Accuracy: {metrics['accuracy']:.4f}")
    print(f"[TRAIN] Precision: {metrics['precision']:.4f}")
    print(f"[TRAIN] Recall:    {metrics['recall']:.4f}")
    print(f"[TRAIN] F1 Score:  {metrics['f1_score']:.4f}")
    print(f"[TRAIN] ROC-AUC:   {metrics['roc_auc']:.4f}")

    # Save artifacts locally
    model_file = os.path.join(model_dir, "model.joblib")
    metrics_file = os.path.join(metrics_dir, "metrics.json")

    joblib.dump(pipeline, model_file)
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"[TRAIN] Artifacts saved to:\n  - {model_file}\n  - {metrics_file}")

    # Optional S3 Upload
    if s3_bucket:
        try:
            import boto3

            s3 = boto3.client("s3")
            s3_model_key = f"models/model_{version}.joblib"
            s3_latest_model_key = "models/model_latest.joblib"
            s3_metrics_key = f"metrics/metrics_{version}.json"
            s3_latest_metrics_key = "metrics/metrics.json"

            print(f"[TRAIN] Uploading model to s3://{s3_bucket}/{s3_model_key}...")
            s3.upload_file(model_file, s3_bucket, s3_model_key)
            s3.upload_file(model_file, s3_bucket, s3_latest_model_key)

            print(f"[TRAIN] Uploading metrics to s3://{s3_bucket}/{s3_latest_metrics_key}...")
            s3.upload_file(metrics_file, s3_bucket, s3_metrics_key)
            s3.upload_file(metrics_file, s3_bucket, s3_latest_metrics_key)
            print("[TRAIN] S3 upload successful!")
        except Exception as e:
            print(f"[TRAIN] S3 upload error: {e}")

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Train Fraud Detection Classifier")
    parser.add_argument("--data-path", type=str, default="data/raw/transactions_v1.csv")
    parser.add_argument("--version", type=str, default="v1")
    parser.add_argument("--model-dir", type=str, default="artifacts/models")
    parser.add_argument("--metrics-dir", type=str, default="artifacts/metrics")
    parser.add_argument("--s3-bucket", type=str, default=None)

    args = parser.parse_args()

    df = load_dataset(args.data_path, args.s3_bucket)
    train_model(
        df=df,
        version=args.version,
        model_dir=args.model_dir,
        metrics_dir=args.metrics_dir,
        s3_bucket=args.s3_bucket,
    )


if __name__ == "__main__":
    main()
