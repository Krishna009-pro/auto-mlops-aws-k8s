"""
Unit Tests for MLOps Pipeline Components.
Tests data generation, model training, and FastAPI inference serving.
"""

import os
import pytest
from fastapi.testclient import TestClient
from src.dataset.generate_data import generate_fraud_data
from src.train.train import train_model
from src.serve.app import app, model_cache


def test_dataset_generation():
    """Verify synthetic dataset generator produces correct schema and values."""
    df = generate_fraud_data(num_samples=100, fraud_rate=0.1, random_seed=42)

    assert len(df) == 100
    assert "is_fraud" in df.columns
    assert "transaction_amount" in df.columns
    assert "device_trust_score" in df.columns
    assert set(df["is_fraud"].unique()).issubset({0, 1})


def test_model_training(tmp_path):
    """Verify model training produces artifacts and valid metrics."""
    df = generate_fraud_data(num_samples=300, fraud_rate=0.1, random_seed=42)
    model_dir = str(tmp_path / "models")
    metrics_dir = str(tmp_path / "metrics")

    metrics = train_model(
        df=df,
        version="test-v1",
        model_dir=model_dir,
        metrics_dir=metrics_dir,
        s3_bucket=None,
    )

    assert os.path.exists(os.path.join(model_dir, "model.joblib"))
    assert os.path.exists(os.path.join(metrics_dir, "metrics.json"))
    assert metrics["accuracy"] > 0.70
    assert "precision" in metrics
    assert "recall" in metrics


def test_api_serving(tmp_path):
    """Verify FastAPI inference endpoint answers predictions correctly."""
    # First train a quick model to populate cache
    df = generate_fraud_data(num_samples=200, fraud_rate=0.1, random_seed=42)
    model_dir = str(tmp_path / "models")
    metrics_dir = str(tmp_path / "metrics")

    train_model(
        df=df,
        version="test-v1",
        model_dir=model_dir,
        metrics_dir=metrics_dir,
        s3_bucket=None,
    )

    import joblib
    model_cache["model"] = joblib.load(os.path.join(model_dir, "model.joblib"))
    model_cache["version"] = "test-v1"

    client = TestClient(app)

    # 1. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["model_loaded"] is True

    # 2. Predict endpoint
    payload = {
        "transaction_amount": 2500.0,
        "transaction_frequency": 12,
        "location_risk_score": 0.95,
        "device_trust_score": 0.10,
        "time_of_day": 3,
        "failed_attempts": 3,
    }
    res_predict = client.post("/predict", json=payload)
    assert res_predict.status_code == 200
    data = res_predict.json()
    assert "is_fraud" in data
    assert "fraud_probability" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]

