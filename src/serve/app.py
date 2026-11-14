"""
FastAPI Model Serving Microservice.
Designed for containerized, high-availability deployment on Kubernetes.
Supports live health checking, metrics reporting, and hot-reload from S3.
"""

import os
import json
import logging
from typing import Optional
from contextlib import asynccontextmanager
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field

# Project root calculation for local templates
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(CURRENT_DIR, "templates", "index.html")

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mlops-serving-api")

# Configuration via environment variables
S3_BUCKET = os.getenv("S3_BUCKET", None)
MODEL_S3_KEY = os.getenv("MODEL_S3_KEY", "models/model_latest.joblib")
METRICS_S3_KEY = os.getenv("METRICS_S3_KEY", "metrics/metrics.json")
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "artifacts/models/model.joblib")
LOCAL_METRICS_PATH = os.getenv("LOCAL_METRICS_PATH", "artifacts/metrics/metrics.json")

# Global in-memory model cache
model_cache = {
    "model": None,
    "version": "unknown",
    "metrics": {},
}


def load_model_from_storage():
    """Loads model from AWS S3 or fallback local path."""
    loaded = False

    # 1. Attempt download from S3
    if S3_BUCKET:
        try:
            import boto3

            logger.info(f"Attempting to download model from s3://{S3_BUCKET}/{MODEL_S3_KEY}...")
            s3 = boto3.client("s3")
            os.makedirs("artifacts/models", exist_ok=True)
            os.makedirs("artifacts/metrics", exist_ok=True)

            target_model = "artifacts/models/model_downloaded.joblib"
            target_metrics = "artifacts/metrics/metrics_downloaded.json"

            s3.download_file(S3_BUCKET, MODEL_S3_KEY, target_model)
            model_cache["model"] = joblib.load(target_model)

            try:
                s3.download_file(S3_BUCKET, METRICS_S3_KEY, target_metrics)
                with open(target_metrics, "r") as f:
                    model_cache["metrics"] = json.load(f)
                    model_cache["version"] = model_cache["metrics"].get("version", "s3-latest")
            except Exception as e:
                logger.warning(f"Could not fetch metrics from S3: {e}")

            loaded = True
            logger.info(f"Model successfully loaded from S3. Version: {model_cache['version']}")
        except Exception as e:
            logger.error(f"Failed to load model from S3: {e}. Falling back to local model.")

    # 2. Fallback to local model
    if not loaded and os.path.exists(LOCAL_MODEL_PATH):
        try:
            logger.info(f"Loading local model from {LOCAL_MODEL_PATH}...")
            model_cache["model"] = joblib.load(LOCAL_MODEL_PATH)
            if os.path.exists(LOCAL_METRICS_PATH):
                with open(LOCAL_METRICS_PATH, "r") as f:
                    model_cache["metrics"] = json.load(f)
                    model_cache["version"] = model_cache["metrics"].get("version", "local-v1")
            loaded = True
            logger.info(f"Local model loaded successfully. Version: {model_cache['version']}")
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")

    if not loaded:
        logger.warning("No model found. Endpoints will return 503 until a model is trained and loaded.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load model
    load_model_from_storage()
    yield
    # Shutdown
    logger.info("Shutting down model serving microservice...")


app = FastAPI(
    title="MLOps Fraud Detection Inference API",
    description="Production-grade, auto-scaling model serving microservice deployed on Kubernetes",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend or dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Schemas for validation
class TransactionRequest(BaseModel):
    transaction_amount: float = Field(..., json_schema_extra={"example": 145.50}, description="Amount of transaction in USD")
    transaction_frequency: int = Field(..., json_schema_extra={"example": 5}, description="Number of transactions today")
    location_risk_score: float = Field(..., ge=0.0, le=1.0, json_schema_extra={"example": 0.25}, description="Geographic anomaly score (0-1)")
    device_trust_score: float = Field(..., ge=0.0, le=1.0, json_schema_extra={"example": 0.88}, description="Device reputation score (0-1)")
    time_of_day: int = Field(..., ge=0, le=23, json_schema_extra={"example": 14}, description="Hour of transaction (0-23)")
    failed_attempts: int = Field(..., ge=0, json_schema_extra={"example": 0}, description="Recent failed authentication attempts")


class PredictionResponse(BaseModel):
    is_fraud: int
    fraud_probability: float
    risk_level: str
    model_version: str
    action_recommended: str


@app.get("/", response_class=HTMLResponse)
def root():
    """Serves the full-stack MLOps web dashboard."""
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>SentinelOps API Online</h1><p>Visit <a href='/docs'>/docs</a> for API docs.</p>")


@app.post("/api/retrain")
def api_retrain_model():
    """
    Simulates automated Continuous Training (CT) and zero-downtime deployment.
    Triggered from the full-stack web UI.
    """
    try:
        from src.dataset.generate_data import generate_fraud_data
        from src.train.train import train_model

        # 1. Generate new drift dataset
        df_new = generate_fraud_data(num_samples=3500, fraud_rate=0.10, drift_factor=0.3, random_seed=99)

        # 2. Train new model version
        version = f"v2.{int(pd.Timestamp.now().timestamp()) % 1000}"
        metrics = train_model(
            df=df_new,
            version=version,
            model_dir="artifacts/models",
            metrics_dir="artifacts/metrics",
            s3_bucket=None,
        )

        # 3. Reload in-memory cache (simulating zero-downtime hot reload)
        model_cache["model"] = joblib.load("artifacts/models/model.joblib")
        model_cache["version"] = version
        model_cache["metrics"] = metrics

        logger.info(f"Model hot-reloaded to version {version} with accuracy {metrics['accuracy']:.4f}")
        return metrics
    except Exception as e:
        logger.error(f"Retraining error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Automated retraining failed: {str(e)}",
        )


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Kubernetes Liveness and Readiness Probe Endpoint.
    Returns 200 if container is healthy and model is loaded.
    """
    is_ready = model_cache["model"] is not None
    return {
        "status": "healthy" if is_ready else "initializing",
        "model_loaded": is_ready,
        "model_version": model_cache["version"],
    }


@app.get("/metrics")
def get_model_metrics():
    """Returns evaluation metrics of currently loaded model."""
    if not model_cache["metrics"]:
        return {"message": "No metrics available for current model."}
    return {
        "model_version": model_cache["version"],
        "metrics": model_cache["metrics"],
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: TransactionRequest):
    """
    Real-time fraud prediction endpoint.
    Takes transaction attributes, returns fraud verdict and probability score.
    """
    model = model_cache["model"]
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not yet loaded or currently initializing.",
        )

    # Convert request to single-row DataFrame
    features = pd.DataFrame([request.model_dump()])

    try:
        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])

        # Determine risk tier
        if probability >= 0.70:
            risk = "HIGH"
            action = "BLOCK_TRANSACTION"
        elif probability >= 0.40:
            risk = "MEDIUM"
            action = "STEP_UP_AUTHENTICATION"
        else:
            risk = "LOW"
            action = "APPROVE"

        logger.info(f"Prediction: Fraud={prediction}, Prob={probability:.4f}, Risk={risk}")

        return PredictionResponse(
            is_fraud=prediction,
            fraud_probability=round(probability, 4),
            risk_level=risk,
            model_version=model_cache["version"],
            action_recommended=action,
        )
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference computation error: {str(e)}",
        )


@app.post("/reload")
def reload_model():
    """
    Hot-reloads model without dropping container connections.
    Useful for manual triggers or rolling webhook updates.
    """
    load_model_from_storage()
    return {
        "status": "reloaded",
        "model_version": model_cache["version"],
        "metrics": model_cache["metrics"],
    }
