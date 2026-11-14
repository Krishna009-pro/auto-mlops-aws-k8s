"""
End-to-End Local Simulation of the Cloud-Native MLOps Automation Pipeline.
Runs the entire lifecycle locally:
  1. Data Ingestion (generates transactions_v1.csv & transactions_v2.csv)
  2. S3 Trigger Simulation (Trigger Lambda validates CSV schema)
  3. Continuous Training (CT) executes training script and computes evaluation metrics
  4. S3 Metrics Upload Simulation (Evaluator Lambda checks quality gate)
  5. Continuous Deployment (CD) performs rolling reload of the model serving API
  6. Live Inference Testing (sends sample transactions to verify predictions)
  7. Automated SNS Alerting simulation
"""

import os
import sys
import time
import json
import logging
from fastapi.testclient import TestClient

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.dataset.generate_data import generate_fraud_data
from src.train.train import train_model
from src.serve.app import app, model_cache

logging.basicConfig(level=logging.INFO, format="%(message)s")


def print_step(step_num: int, title: str):
    print("\n" + "=" * 70)
    print(f"  STEP {step_num}: {title.upper()}")
    print("=" * 70)


def run_simulation():
    print("""
    ======================================================================
      CLOUD-NATIVE MLOps AUTOMATED PIPELINE: LOCAL END-TO-END SIMULATION
    ======================================================================
    Tech Stack: Python, Docker, Kubernetes, AWS S3, Lambda, SNS, EC2, IAM
    """)

    # -------------------------------------------------------------
    # Step 1: Initial Data Generation (v1)
    # -------------------------------------------------------------
    print_step(1, "Data Ingestion Simulation (Initial v1 Dataset)")
    raw_dir = os.path.join(PROJECT_ROOT, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    v1_path = os.path.join(raw_dir, "transactions_v1.csv")

    df_v1 = generate_fraud_data(num_samples=2500, fraud_rate=0.08, drift_factor=0.0, random_seed=42)
    df_v1.to_csv(v1_path, index=False)
    print(f"[OK] Generated {len(df_v1)} records for transactions_v1.csv")
    print(f"     Target 'is_fraud' distribution: {dict(df_v1['is_fraud'].value_counts())}")

    # -------------------------------------------------------------
    # Step 2: S3 Ingestion Trigger (Lambda 1 Simulation)
    # -------------------------------------------------------------
    print_step(2, "Serverless Ingestion Trigger (AWS Lambda 1)")
    print("[SIMULATION] S3 Event: ObjectCreated -> s3://mlops-bucket/datasets/transactions_v1.csv")
    print("[LAMBDA 1] Checking CSV schema headers...")
    expected_cols = [
        "transaction_amount",
        "transaction_frequency",
        "location_risk_score",
        "device_trust_score",
        "time_of_day",
        "failed_attempts",
        "is_fraud",
    ]
    missing = [c for c in expected_cols if c not in df_v1.columns]
    if missing:
        print(f"[ERROR] Missing columns: {missing}")
        return
    print("[LAMBDA 1] Schema validation: PASSED (7/7 columns valid)")
    print("[LAMBDA 1] Dispatching Kubernetes Batch Training Job (mlops-training-job)...")
    print("[SNS ALERT] Message sent: 'New dataset ingested. Training job initiated on EC2 cluster.'")

    # -------------------------------------------------------------
    # Step 3: Model Training on Kubernetes Worker (CT)
    # -------------------------------------------------------------
    print_step(3, "Continuous Training (CT) on Kubernetes Pod")
    model_dir = os.path.join(PROJECT_ROOT, "artifacts", "models")
    metrics_dir = os.path.join(PROJECT_ROOT, "artifacts", "metrics")

    print("[POD] Training Random Forest model with StandardScaler pipeline...")
    metrics_v1 = train_model(
        df=df_v1,
        version="v1.0",
        model_dir=model_dir,
        metrics_dir=metrics_dir,
        s3_bucket=None,
    )

    # -------------------------------------------------------------
    # Step 4: Model Evaluation Quality Gate (Lambda 2 Simulation)
    # -------------------------------------------------------------
    print_step(4, "Model Quality Gate & CD (AWS Lambda 2 + SSM)")
    print("[SIMULATION] S3 Event: ObjectCreated -> s3://mlops-bucket/metrics/metrics.json")
    print(f"[LAMBDA 2] Reading metrics for model version: {metrics_v1['version']}")
    print(f"           Trained Accuracy: {metrics_v1['accuracy']:.4f}")
    print(f"           Trained F1-Score: {metrics_v1['f1_score']:.4f}")

    threshold = 0.85
    print(f"[SSM PARAMETER STORE] Current Baseline Accuracy Threshold: {threshold:.2f}")

    if metrics_v1["accuracy"] >= threshold:
        print("[GATE] Quality Gate Status: APPROVED FOR PRODUCTION")
        print("[CD] Updating Kubernetes Deployment 'mlops-serving-api' (Rolling Update)...")
        print("[SNS ALERT] SUCCESS: Model v1.0 promoted to production. Accuracy: " f"{metrics_v1['accuracy']:.4f}")
    else:
        print("[GATE] Quality Gate Status: REJECTED")
        return

    # -------------------------------------------------------------
    # Step 5: Live Model Serving & Inference API
    # -------------------------------------------------------------
    print_step(5, "Live Model Serving (FastAPI on Kubernetes)")
    # Load model into serving cache
    import joblib
    model_cache["model"] = joblib.load(os.path.join(model_dir, "model.joblib"))
    model_cache["version"] = metrics_v1["version"]
    model_cache["metrics"] = metrics_v1

    client = TestClient(app)

    # Health check
    res_health = client.get("/health")
    print(f"[API] Health Check: {res_health.json()}")

    # Test Sample Transactions
    print("\n[API] Testing Sample Real-Time Predictions:")

    # Transaction A: Normal user
    tx_normal = {
        "transaction_amount": 32.50,
        "transaction_frequency": 2,
        "location_risk_score": 0.12,
        "device_trust_score": 0.95,
        "time_of_day": 14,
        "failed_attempts": 0,
    }
    res_a = client.post("/predict", json=tx_normal).json()
    print(f"\n  Transaction A (Normal Grocery Purchase):")
    print(f"    - Fraud Verdict: {res_a['is_fraud']} | Probability: {res_a['fraud_probability']:.2%}")
    print(f"    - Risk Level: {res_a['risk_level']} | Action: {res_a['action_recommended']}")

    # Transaction B: Suspicious high risk
    tx_fraud = {
        "transaction_amount": 2890.00,
        "transaction_frequency": 14,
        "location_risk_score": 0.98,
        "device_trust_score": 0.05,
        "time_of_day": 3,
        "failed_attempts": 4,
    }
    res_b = client.post("/predict", json=tx_fraud).json()
    print(f"\n  Transaction B (Suspicious 3 AM Overseas Large Transfer):")
    print(f"    - Fraud Verdict: {res_b['is_fraud']} | Probability: {res_b['fraud_probability']:.2%}")
    print(f"    - Risk Level: {res_b['risk_level']} | Action: {res_b['action_recommended']}")

    # -------------------------------------------------------------
    # Step 6: Retraining Loop Simulation (New Data v2 with Drift)
    # -------------------------------------------------------------
    print_step(6, "Simulating Automated Retraining Loop (v2 Drift Data)")
    print("[DATA-ENGINEER] New batch of transactions uploaded to S3: transactions_v2.csv")
    df_v2 = generate_fraud_data(num_samples=3500, fraud_rate=0.10, drift_factor=0.3, random_seed=99)
    v2_path = os.path.join(raw_dir, "transactions_v2.csv")
    df_v2.to_csv(v2_path, index=False)

    print("[EVENT] S3 Trigger -> Lambda 1 -> Kubernetes Job -> Training model v2.0...")
    metrics_v2 = train_model(
        df=df_v2,
        version="v2.0",
        model_dir=model_dir,
        metrics_dir=metrics_dir,
        s3_bucket=None,
    )

    print(f"\n[EVALUATE] Model v1.0 Accuracy: {metrics_v1['accuracy']:.4f}")
    print(f"[EVALUATE] Model v2.0 Accuracy: {metrics_v2['accuracy']:.4f}")

    if metrics_v2["accuracy"] >= metrics_v1["accuracy"]:
        print("[DECISION] Model v2.0 is superior! Triggering zero-downtime rolling update.")
        model_cache["model"] = joblib.load(os.path.join(model_dir, "model.joblib"))
        model_cache["version"] = metrics_v2["version"]
        model_cache["metrics"] = metrics_v2
        print(f"[LIVE UPDATE] Kubernetes serving pods now actively routing traffic to Model {model_cache['version']}")
        print(f"[SNS ALERT] Email sent: 'Model v2.0 automatically deployed with {metrics_v2['accuracy']:.4f} accuracy.'")

    print("\n" + "=" * 70)
    print("  SIMULATION COMPLETE: ALL MLOps AUTOMATION LOOPS FUNCTIONING PERFECTLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_simulation()
