import http.server
import threading
import subprocess
import time
import os
from PIL import Image
import numpy as np

BASE_DIR = r"k:\Degree\Sem 5\Cloud-Native MLOps\Practicals\mlops-automated-pipeline"
DIAGRAMS_DIR = os.path.join(BASE_DIR, "docs", "diagrams")
ARTIFACT_DIR = r"C:\Users\kkp18\.gemini\antigravity\brain\b79467d7-9886-423e-abc5-5fa34156e482"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PORT = 9123

html_template = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="/mermaid.min.js"></script>
  <style>
    body {
      margin: 0;
      padding: 40px;
      background-color: #18181b;
      display: inline-block;
      font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
    }
    .mermaid-box {
      background-color: #18181b;
      border: 1px solid #27272a;
      border-radius: 14px;
      padding: 30px;
      display: inline-block;
    }
  </style>
  <script>
    mermaid.initialize({
      startOnLoad: true,
      theme: 'dark',
      themeVariables: {
        darkMode: true,
        background: '#18181b',
        mainBkg: '#27272a',
        textColor: '#f4f4f5',
        lineColor: '#a1a1aa'
      }
    });
  </script>
</head>
<body>
  <div class="mermaid-box">
    <pre class="mermaid">
__CODE__
    </pre>
  </div>
</body>
</html>"""

arch_code = """flowchart TD
    subgraph ClientTier["1. CLIENT TIER (User & Interface)"]
        UI["Web UI Dashboard (SentinelOps)"]
        XAI["Explainable AI Panel (Risk Indicators)"]
        Audit["Live Transaction Audit Stream"]
    end

    subgraph ComputeTier["2. COMPUTE TIER (AWS EC2 + Kubernetes K3s)"]
        NP["Kubernetes NodePort (30080 -> 8000)"]
        SVC["K8s Service: fraud-detector-service"]
        POD_SERV["Serving Pod (FastAPI + RandomForest + KS-Test)"]
        POD_TRAIN["Training Job Pod (Scikit-Learn Batch Job)"]
        CFG["ConfigMap & IAM Role: MLOpsEC2Role"]
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

    %% Connections
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
    GH --> GHA --> DH"""

seq_code = """sequenceDiagram
    autonumber
    actor User as Client / Web UI
    participant Srv as FastAPI Serving (K3s Pod)
    participant ML as RandomForest Model (XAI)
    participant Drift as Drift Monitor (KS-Test)
    participant S3 as AWS S3 Bucket
    participant Lambda as AWS Lambda (MLOpsProcessor)
    participant SNS as AWS SNS (mlops-alerts)
    participant K8s as K8s Training Job

    Note over User,Srv: 1. Real-Time Online Inference Phase
    User->>Srv: POST /predict (Amount, Location, Device)
    Srv->>ML: Extract features & evaluate weights
    ML-->>Srv: Return Fraud Prob (88%) + Explainable Risk Factors
    Srv-->>User: Render Decision, Risk Factors & Live Audit Row
    Srv->>Drift: Append transaction to in-memory sliding buffer

    Note over Drift,S3: 2. Continuous Monitoring & Drift Trigger
    Drift->>Drift: Run Kolmogorov-Smirnov Test (p-value < 0.05)
    Drift->>S3: Export drifted dataset to s3://icem-mlops-krishna250/datasets/

    Note over S3,K8s: 3. Serverless Event-Driven Orchestration
    S3->>Lambda: Trigger s3:ObjectCreated:Put Event
    Lambda->>Lambda: Validate schema, data types & row count (242ms)
    Lambda->>K8s: Launch batch training job (fraud-trainer)
    K8s->>K8s: Train RandomForest with balanced weights
    K8s->>S3: Upload model_v2.joblib & metrics.json to models/
    S3->>Lambda: Event: Evaluation metrics ready

    Note over Lambda,SNS: 4. Automated Quality Gate & Deployment
    Lambda->>Lambda: Evaluate Gate: Accuracy >= 0.85 & F1 >= 0.80
    Lambda->>SNS: Publish deployment verdict & metric report
    SNS-->>User: Dispatch Email / SMS alert to DevOps Engineer
    Lambda->>Srv: Zero-downtime rolling update (kubectl rollout restart)
    Srv->>Srv: Hot-swap model in memory with zero dropped requests"""

def render_all():
    # Write HTML files
    with open(os.path.join(DIAGRAMS_DIR, "render_arch.html"), "w", encoding="utf-8") as f:
        f.write(html_template.replace("__CODE__", arch_code))
    with open(os.path.join(DIAGRAMS_DIR, "render_seq.html"), "w", encoding="utf-8") as f:
        f.write(html_template.replace("__CODE__", seq_code))

    # Start local HTTP server with correct directory
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIAGRAMS_DIR, **kwargs)
        def log_message(self, format, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", PORT), QuietHandler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()

    tasks = [
        ("render_arch.html", "system_architecture_mermaid_dark.png", 2200, 1800),
        ("render_seq.html", "sequence_diagram_mermaid_dark.png", 2400, 1800),
    ]

    for html_file, out_name, w, h in tasks:
        raw_out = os.path.join(DIAGRAMS_DIR, "raw_" + out_name)
        final_out = os.path.join(DIAGRAMS_DIR, out_name)

        cmd = [
            EDGE_PATH,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={w},{h}",
            "--virtual-time-budget=4000",
            f"--screenshot={raw_out}",
            f"http://127.0.0.1:{PORT}/{html_file}"
        ]
        subprocess.run(cmd, check=True)

        # Crop to content
        im = Image.open(raw_out)
        gray = im.convert("L")
        arr = np.array(gray)
        rows = np.where(arr > 30)[0]
        cols = np.where(arr > 30)[1]

        if len(rows) > 0 and len(cols) > 0:
            pad = 20
            c_min = max(0, cols.min() - pad)
            r_min = max(0, rows.min() - pad)
            c_max = min(im.width, cols.max() + pad)
            r_max = min(im.height, rows.max() + pad)
            cropped = im.crop((c_min, r_min, c_max, r_max))
            cropped.save(final_out)
            print(f"Successfully generated {out_name}: {cropped.size}")
        else:
            im.save(final_out)
            print(f"Generated {out_name}: {im.size}")

        # Also copy to brain artifact dir
        import shutil
        shutil.copy(final_out, os.path.join(ARTIFACT_DIR, out_name))

    server.shutdown()
    print("All Mermaid diagrams rendered!")

if __name__ == "__main__":
    render_all()
