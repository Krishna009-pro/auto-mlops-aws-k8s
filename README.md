# Cloud-Native MLOps Automation Platform (CI/CD/CT)

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, event-driven **MLOps Automation Platform** designed for continuous model lifecycle management: **Continuous Integration (CI)**, **Continuous Training (CT)**, **Continuous Deployment (CD)**, and **Continuous Monitoring (CM)**.

---

## 📌 Architecture & Automated Workflow

```
[Data Engineer / Ingest]
        │
        ▼ (New CSV dataset)
    [AWS S3] (datasets/transactions_v2.csv)
        │
        ▼ (S3 Event / EventBridge)
   [AWS Lambda 1] ──(Validates Schema & triggers)──► [K8s Training Job (on EC2)]
  (Ingest Trigger)                                           │
                                                             ▼ (Pulls Python Trainer
                                                                from Docker Hub)
                                                        [Trains Model]
                                                             │
                                                             ▼ (Uploads model.joblib & metrics.json)
                                                         [AWS S3]
                                                             │
                                                             ▼ (S3 Event)
   [AWS SNS Alerts] ◄── [AWS Lambda 2] ────────────────► [Kubernetes Cluster]
  (Email Notification)   (Evaluator + SSM Parameter)   (Rolling Update on Serving Pods)
```

---

## 🛠️ Tech Stack & Service Attribution

| Technology / Service | Role in MLOps Automation |
| :--- | :--- |
| **Python 3.11** | Machine Learning pipeline (Scikit-Learn, Random Forest), data generation, and FastAPI inference engine. |
| **Git & GitHub** | Source code versioning and automated CI pipeline with GitHub Actions. |
| **Docker & Docker Hub** | Multi-container packaging for the **Trainer** job and **Serving** microservice. |
| **AWS EC2** | Compute instances hosting the Kubernetes worker nodes. |
| **Kubernetes (EKS / K3s)** | Orchestrates batch training jobs and provides zero-downtime rolling updates for the model serving API. |
| **AWS S3** | Ingestion lake for raw datasets, model artifact registry, and evaluation metrics store. |
| **AWS Lambda** | Serverless orchestrators: Schema validation (Ingestion trigger) and Quality gate evaluation. |
| **AWS SNS** | Automated notification engine sending email reports on model performance and deployments. |
| **AWS IAM** | Zero-trust security: IRSA (IAM Roles for Service Accounts) and least-privilege Lambda policies. |
| **AWS SSM Parameter Store** | Stores dynamic configuration (model accuracy thresholds and active production version tags). |
| **AWS CloudWatch** | Structured logging and metric telemetry for inference latency and Lambda execution. |

---

## 🚀 The 4 Automated Loops

### 1. Continuous Integration (CI)
- Whenever code is pushed to `main`, **GitHub Actions** runs syntax linting (`flake8`), executes unit tests (`pytest`), builds Docker images, and pushes them to **Docker Hub**.

### 2. Continuous Training (CT)
- Uploading a new dataset (`transactions_v2.csv`) to S3 triggers **AWS Lambda 1**.
- Lambda checks schema validity (columns, nulls, data types) and launches an ephemeral **Kubernetes Training Job**.
- The job pulls the trainer container, fits the Random Forest model with feature scaling, and pushes `model.joblib` and `metrics.json` back to S3.

### 3. Continuous Deployment (CD)
- Upload of `metrics.json` triggers **AWS Lambda 2**.
- Lambda reads the target accuracy threshold from **AWS SSM Parameter Store**.
- **Quality Gate:** If `new_accuracy >= threshold` (e.g. 0.85):
  - Lambda updates the SSM production parameter.
  - Triggers a **zero-downtime rolling update** (`maxSurge: 1, maxUnavailable: 0`) on Kubernetes.
  - If the gate fails, deployment is aborted, preserving the current stable model.

### 4. Continuous Monitoring & Alerting (CM)
- **AWS SNS** immediately publishes an email summary to subscribers with evaluation metrics (Accuracy, Precision, Recall, F1) and deployment verdicts.

---

## 📂 Project Structure

```
mlops-automated-pipeline/
├── .github/
│   └── workflows/
│       └── ci-cd.yaml                   # GitHub Actions CI/CD Pipeline
├── src/
│   ├── dataset/
│   │   └── generate_data.py             # Synthetic fraud data generator (v1 & v2 drift)
│   ├── train/
│   │   ├── train.py                     # ML Training script & metric logger
│   │   ├── Dockerfile                   # Dockerfile for training container
│   │   └── requirements.txt
│   └── serve/
│       ├── app.py                       # FastAPI model serving microservice
│       ├── Dockerfile                   # Dockerfile for serving container
│       └── requirements.txt
├── k8s/
│   ├── namespace.yaml                   # Kubernetes namespace (mlops)
│   ├── configmap.yaml                   # S3 and AWS configuration
│   ├── serviceaccount-irsa.yaml         # IAM Roles for Service Accounts (IRSA)
│   ├── deployment.yaml                  # 2-replica Deployment with rolling updates
│   ├── service.yaml                     # NodePort / LoadBalancer service
│   └── training-job.yaml                # Batch Job definition for model training
├── aws/
│   ├── lambda/
│   │   ├── trigger_training/            # S3 Ingest trigger function
│   │   └── evaluate_and_deploy/         # Quality Gate & Deployment function
│   ├── iam/
│   │   ├── lambda_execution_policy.json # IAM policy for Lambda
│   │   └── ec2_k8s_node_policy.json     # IAM policy for EC2 K8s nodes
│   └── sns/
│       └── setup_sns.py                 # SNS topic & email subscription provisioning
├── tests/
│   └── test_pipeline.py                 # Automated unit tests
├── scripts/
│   ├── simulate_pipeline.py             # Complete local end-to-end simulation
│   ├── build_docker.ps1                 # Docker build helper
│   └── deploy_k8s.ps1                   # Kubernetes deployment helper
├── requirements.txt                     # Root dependencies
└── README.md
```

---

## ⚡ Quickstart: Running the Local Simulation

You can test the entire automated MLOps loop locally in 10 seconds:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full end-to-end pipeline simulation
python scripts/simulate_pipeline.py
```

This runs all 6 stages sequentially and prints live logs for data ingestion, schema validation, model training, quality gate evaluation, rolling reload, and real-time inference predictions.

---

## 🐳 Docker Build & Execution

### 1. Build and Tag Images
```powershell
.\scripts\build_docker.ps1 -DockerUser yourdockerhub -Tag latest
```

### 2. Run the Serving Container Locally
```bash
docker run -p 8000:8000 yourdockerhub/mlops-serving:latest
```
Visit the interactive Swagger UI at: `http://localhost:8000/docs`

---

## ☸️ Kubernetes Deployment

Deploy all components into your local or cloud Kubernetes cluster:

```powershell
.\scripts\deploy_k8s.ps1 -Namespace mlops -DockerUser yourdockerhub
```

Check running pods and services:
```bash
kubectl get pods,svc -n mlops
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Kubernetes Liveness/Readiness probe endpoint. |
| `GET` | `/metrics` | Returns evaluation metrics (Accuracy, F1, ROC-AUC) of active model. |
| `POST` | `/predict` | Real-time fraud classification and probability score. |
| `POST` | `/reload` | Hot-reloads updated model artifact from storage without container restart. |

### Sample Prediction Request:
```json
POST /predict
{
  "transaction_amount": 2500.00,
  "transaction_frequency": 12,
  "location_risk_score": 0.95,
  "device_trust_score": 0.10,
  "time_of_day": 3,
  "failed_attempts": 4
}
```

### Sample Response:
```json
{
  "is_fraud": 1,
  "fraud_probability": 0.9421,
  "risk_level": "HIGH",
  "model_version": "v2.0",
  "action_recommended": "BLOCK_TRANSACTION"
}
```

---

## 🎓 Examination & Viva Key Talking Points

1. **Why use Kubernetes Jobs instead of running training inside the web app container?**
   - *Answer:* Separation of concerns. Model training is compute-heavy and memory-intensive; running it inside the API pod would starve inference traffic. Kubernetes Batch Jobs are ephemeral—they spin up on demand, train, and release resources.

2. **Why use AWS Lambda as an event-driven trigger instead of cron jobs?**
   - *Answer:* Event-driven serverless architecture saves cloud costs. Lambda incurs zero cost while idle and triggers within milliseconds of new data landing in S3.

3. **How is security handled across Kubernetes and AWS?**
   - *Answer:* We avoid hardcoded AWS access keys using **IAM Roles for Service Accounts (IRSA)**. The Kubernetes ServiceAccount is annotated with an IAM Role ARN, allowing pods to retrieve temporary credentials via STS.

4. **What prevents a degraded model from reaching production?**
   - *Answer:* The Evaluator Lambda acts as an automated Quality Gate. It verifies `new_accuracy >= threshold` (stored in AWS SSM Parameter Store). If the model regresses, deployment is blocked and an alert is sent via AWS SNS.
