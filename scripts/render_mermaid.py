import os
import subprocess
import time

BASE_DIR = r"k:\Degree\Sem 5\Cloud-Native MLOps\Practicals\mlops-automated-pipeline"
DIAGRAMS_DIR = os.path.join(BASE_DIR, "docs", "diagrams")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

html_template = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    body {
      margin: 0;
      padding: 40px;
      background-color: #ffffff;
      font-family: Inter, system-ui, -apple-system, sans-serif;
      display: inline-block;
    }
    .mermaid {
      background: white;
    }
  </style>
  <script>
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      themeVariables: {
        fontSize: '16px',
        fontFamily: 'Inter, system-ui, sans-serif',
        primaryColor: '#e0f2fe',
        primaryBorderColor: '#0284c7',
        primaryTextColor: '#0f172a',
        lineColor: '#0284c7',
        secondaryColor: '#f0fdf4',
        secondaryBorderColor: '#16a34a',
        tertiaryColor: '#f8fafc',
        tertiaryBorderColor: '#94a3b8'
      }
    });
  </script>
</head>
<body>
  <div class="mermaid">
__MERMAID_CODE__
  </div>
</body>
</html>
"""

arch_mermaid = """flowchart TD
    subgraph ClientTier["1. CLIENT TIER (User & Web Dashboard)"]
        UI["Web UI Dashboard (SentinelOps)"]
        XAI["Explainable AI Panel (Risk Indicators)"]
        Audit["Live Transaction Audit Stream"]
    end

    subgraph ComputeTier["2. COMPUTE TIER (AWS EC2 + Kubernetes K3s)"]
        NP["Kubernetes NodePort (30080 to 8000)"]
        SVC["K8s Service: fraud-detector-service"]
        POD_SERV["Serving Pod (FastAPI + RandomForest + KS-Test)"]
        POD_TRAIN["Training Job Pod (Scikit-Learn Batch Job)"]
        CFG["ConfigMap and IAM Role: MLOpsEC2Role"]
    end

    subgraph StorageTier["3. STORAGE & REGISTRY (AWS S3: icem-mlops-krishna250)"]
        S3_DATA["datasets/ (transactions_v1.csv, transactions_v2.csv)"]
        S3_MODELS["models/ (model.joblib, model_v2.joblib)"]
        S3_METRICS["metrics/ (summary_*.json, confusion matrices)"]
    end

    subgraph ServerlessTier["4. SERVERLESS & MONITORING (AWS Cloud)"]
        LAMBDA["AWS Lambda: MLOpsProcessor (Validation & Trigger)"]
        SNS["AWS SNS Topic: mlops-alerts (Email Notifications)"]
        CW["Amazon CloudWatch (Logs & Execution Metrics)"]
    end

    subgraph CICDTier["5. CI/CD & REGISTRY TIER"]
        GH["GitHub: auto-mlops-aws-k8s"]
        GHA["GitHub Actions (Lint, Test, Docker Build)"]
        DH["Docker Hub: krishna250/mlops-serving & training"]
    end

    UI -->|HTTP POST :30080| NP
    NP --> SVC
    SVC --> POD_SERV
    POD_SERV -->|Syncs Drifted CSV| S3_DATA
    S3_DATA -->|s3:ObjectCreated Put Event| LAMBDA
    LAMBDA -->|Triggers Retraining Job| POD_TRAIN
    POD_TRAIN -->|Uploads Model & Metrics| S3_MODELS
    POD_TRAIN -->|Saves Evaluation JSON| S3_METRICS
    S3_METRICS -->|Triggers Quality Gate| LAMBDA
    LAMBDA -->|Dispatches Alerts| SNS
    SNS -->|Sends Email Notification| UserEmail["DevOps / MLOps Engineers"]
    LAMBDA -->|Rollout Restart| POD_SERV
    DH -->|Pulls Container Images| POD_SERV
    DH -->|Pulls Training Container| POD_TRAIN
    GH --> GHA --> DH
"""

def render():
    html_file = os.path.join(DIAGRAMS_DIR, "system_architecture_mermaid.html")
    png_file = os.path.join(DIAGRAMS_DIR, "system_architecture_mermaid.png")
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_template.replace("__MERMAID_CODE__", arch_mermaid))
    
    print(f"Wrote {html_file}")
    
    # Run Edge headless to capture screenshot
    cmd = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1650,1450",
        f"--screenshot={png_file}",
        html_file
    ]
    subprocess.run(cmd, check=True)
    print(f"Captured {png_file}")

if __name__ == "__main__":
    render()
