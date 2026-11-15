"""
SentinelOps - Clean, High-Contrast Light Theme Architecture Diagram
Renders the exact clean, simple, highly understandable layout of the Mermaid flowchart
with crisp white background, pastel tiered containers, and clear bold connectors.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUTPUT_DIR = r"k:\Degree\Sem 5\Cloud-Native MLOps\Practicals\mlops-automated-pipeline\docs\diagrams"
ARTIFACT_DIR = r"C:\Users\kkp18\.gemini\antigravity\brain\b79467d7-9886-423e-abc5-5fa34156e482"

def create_clean_architecture():
    fig, ax = plt.subplots(figsize=(18, 12), dpi=300)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # Clean Header
    ax.text(9.0, 11.5, "SentinelOps: Cloud-Native System Architecture",
            ha="center", va="center", color="#0f172a", fontsize=18, fontweight="bold")
    ax.text(9.0, 11.1, "Simple High-Level 5-Tier Overview: Ingestion, Compute, Storage, Serverless & CI/CD",
            ha="center", va="center", color="#475569", fontsize=11)

    # Palette - Clean light theme matching Mermaid neutral/default
    BG_CLIENT = "#f0f9ff"      # Sky blue soft
    BORDER_CLIENT = "#0284c7"
    BG_COMPUTE = "#f0fdf4"     # Emerald soft
    BORDER_COMPUTE = "#16a34a"
    BG_STORAGE = "#fffbeb"     # Amber soft
    BORDER_STORAGE = "#d97706"
    BG_SERVERLESS = "#faf5ff"  # Purple soft
    BORDER_SERVERLESS = "#9333ea"
    BG_CICD = "#f8fafc"        # Slate soft
    BORDER_CICD = "#475569"

    BOX_FILL = "#ffffff"
    BOX_BORDER = "#cbd5e1"
    TEXT_MAIN = "#0f172a"
    TEXT_SUB = "#475569"

    # 1. CLIENT TIER (Top Left)
    c_tier = FancyBboxPatch((0.8, 6.2), 3.2, 4.2, boxstyle="round,pad=0.12,rounding_size=0.15",
                            facecolor=BG_CLIENT, edgecolor=BORDER_CLIENT, linewidth=1.8)
    ax.add_patch(c_tier)
    ax.text(2.4, 10.0, "1. CLIENT TIER", ha="center", va="center", color=BORDER_CLIENT, fontsize=11, fontweight="bold")
    ax.text(2.4, 9.6, "(User & Web Dashboard)", ha="center", va="center", color=TEXT_SUB, fontsize=8)

    client_nodes = [
        ("Web UI Dashboard", "SentinelOps Single Page App", 8.8),
        ("Explainable AI Panel", "Feature Impact & Risk Badges", 7.8),
        ("Live Audit Stream", "Dual-Layer LocalStorage Buffer", 6.8),
    ]
    for title, desc, y in client_nodes:
        b = FancyBboxPatch((1.0, y - 0.35), 2.8, 0.7, boxstyle="round,pad=0.06,rounding_size=0.08",
                           facecolor=BOX_FILL, edgecolor=BOX_BORDER, linewidth=1)
        ax.add_patch(b)
        ax.text(2.4, y + 0.08, title, ha="center", va="center", color=TEXT_MAIN, fontsize=8.5, fontweight="bold")
        ax.text(2.4, y - 0.16, desc, ha="center", va="center", color=TEXT_SUB, fontsize=7)

    # 2. COMPUTE TIER (Top Center - Kubernetes on EC2)
    k_tier = FancyBboxPatch((4.5, 4.8), 7.2, 5.6, boxstyle="round,pad=0.12,rounding_size=0.15",
                            facecolor=BG_COMPUTE, edgecolor=BORDER_COMPUTE, linewidth=1.8)
    ax.add_patch(k_tier)
    ax.text(8.1, 10.0, "2. COMPUTE TIER (AWS EC2 + Kubernetes K3s)",
            ha="center", va="center", color=BORDER_COMPUTE, fontsize=11, fontweight="bold")
    ax.text(8.1, 9.6, "Host: t3.medium Ubuntu 24.04  |  NodePort Ingress: 30080",
            ha="center", va="center", color=TEXT_SUB, fontsize=8)

    # NodePort & Service
    b_np = FancyBboxPatch((4.8, 8.4), 6.6, 0.8, boxstyle="round,pad=0.06,rounding_size=0.08",
                          facecolor=BOX_FILL, edgecolor=BORDER_CLIENT, linewidth=1.2)
    ax.add_patch(b_np)
    ax.text(8.1, 8.9, "Kubernetes NodePort: 30080 -> Service: fraud-detector-service",
            ha="center", va="center", color=TEXT_MAIN, fontsize=8.5, fontweight="bold")
    ax.text(8.1, 8.6, "External HTTP Gateway & Cluster Load Balancer",
            ha="center", va="center", color=BORDER_CLIENT, fontsize=7)

    # Serving Pod
    b_sp = FancyBboxPatch((4.8, 6.2), 3.1, 1.9, boxstyle="round,pad=0.06,rounding_size=0.08",
                          facecolor=BOX_FILL, edgecolor=BORDER_COMPUTE, linewidth=1.2)
    ax.add_patch(b_sp)
    ax.text(6.35, 7.7, "Serving Pod (Deployment)", ha="center", va="center", color=BORDER_COMPUTE, fontsize=8.5, fontweight="bold")
    ax.text(6.35, 7.35, "• FastAPI Web Application", ha="center", va="center", color=TEXT_MAIN, fontsize=7.5)
    ax.text(6.35, 7.0, "• RandomForest Classifier", ha="center", va="center", color=TEXT_SUB, fontsize=7)
    ax.text(6.35, 6.65, "• Health Probes: /health", ha="center", va="center", color=TEXT_SUB, fontsize=7)
    ax.text(6.35, 6.35, "• Drift Monitor (KS-Test)", ha="center", va="center", color="#b45309", fontsize=7, fontweight="bold")

    # Training Job Pod
    b_tp = FancyBboxPatch((8.3, 6.2), 3.1, 1.9, boxstyle="round,pad=0.06,rounding_size=0.08",
                          facecolor=BOX_FILL, edgecolor=BORDER_SERVERLESS, linewidth=1.2)
    ax.add_patch(b_tp)
    ax.text(9.85, 7.7, "Training Job (Ephemeral Pod)", ha="center", va="center", color=BORDER_SERVERLESS, fontsize=8.5, fontweight="bold")
    ax.text(9.85, 7.35, "• Batch Job: fraud-trainer", ha="center", va="center", color=TEXT_MAIN, fontsize=7.5)
    ax.text(9.85, 7.0, "• Retrains Model on Drift", ha="center", va="center", color=TEXT_SUB, fontsize=7)
    ax.text(9.85, 6.65, "• Evaluates Quality Gate (>=85%)", ha="center", va="center", color=TEXT_SUB, fontsize=7)
    ax.text(9.85, 6.35, "• Exits & Auto-Terminates (0)", ha="center", va="center", color=BORDER_CLIENT, fontsize=7)

    # ConfigMap
    b_cfg = FancyBboxPatch((4.8, 5.0), 6.6, 0.9, boxstyle="round,pad=0.06,rounding_size=0.08",
                           facecolor=BOX_FILL, edgecolor=BOX_BORDER, linewidth=1)
    ax.add_patch(b_cfg)
    ax.text(8.1, 5.55, "ConfigMap (S3_BUCKET, REGION) & IAM Role (MLOpsEC2Role)",
            ha="center", va="center", color=TEXT_MAIN, fontsize=8, fontweight="bold")
    ax.text(8.1, 5.25, "Zero-credential S3 & SNS authentication via EC2 Instance Profile",
            ha="center", va="center", color=TEXT_SUB, fontsize=7)

    # 3. STORAGE & REGISTRY (Top Right - AWS S3)
    s_tier = FancyBboxPatch((12.2, 6.8), 5.0, 3.6, boxstyle="round,pad=0.12,rounding_size=0.15",
                            facecolor=BG_STORAGE, edgecolor=BORDER_STORAGE, linewidth=1.8)
    ax.add_patch(s_tier)
    ax.text(14.7, 10.0, "3. STORAGE & REGISTRY", ha="center", va="center", color=BORDER_STORAGE, fontsize=11, fontweight="bold")
    ax.text(14.7, 9.6, "AWS S3: icem-mlops-krishna250", ha="center", va="center", color=TEXT_SUB, fontsize=8)

    s3_items = [
        ("datasets/", "Raw & Drifted CSVs (transactions_v1, v2)", 8.9),
        ("models/", "Model Weights & Artifacts (model_v2.joblib)", 8.1),
        ("metrics/", "Evaluation Summaries (summary_*.json)", 7.3),
    ]
    for title, desc, y in s3_items:
        b = FancyBboxPatch((12.4, y - 0.28), 4.6, 0.6, boxstyle="round,pad=0.06,rounding_size=0.08",
                           facecolor=BOX_FILL, edgecolor=BOX_BORDER, linewidth=1)
        ax.add_patch(b)
        ax.text(14.7, y + 0.08, title, ha="center", va="center", color=TEXT_MAIN, fontsize=8.5, fontweight="bold")
        ax.text(14.7, y - 0.14, desc, ha="center", va="center", color=TEXT_SUB, fontsize=7)

    # 4. SERVERLESS & MONITORING (Bottom Right - Lambda & SNS)
    srv_tier = FancyBboxPatch((12.2, 1.8), 5.0, 4.4, boxstyle="round,pad=0.12,rounding_size=0.15",
                             facecolor=BG_SERVERLESS, edgecolor=BORDER_SERVERLESS, linewidth=1.8)
    ax.add_patch(srv_tier)
    ax.text(14.7, 5.8, "4. SERVERLESS & ALERTS (AWS Cloud)",
            ha="center", va="center", color=BORDER_SERVERLESS, fontsize=11, fontweight="bold")
    ax.text(14.7, 5.4, "Event-Driven Automation Core", ha="center", va="center", color=TEXT_SUB, fontsize=8)

    srv_items = [
        ("AWS Lambda: MLOpsProcessor", "Sub-second schema validation & CT trigger (242ms)", 4.6),
        ("AWS SNS: mlops-alerts", "Automated email alerts dispatched to engineers", 3.6),
        ("Amazon CloudWatch", "Centralized execution telemetry & container logs", 2.6),
    ]
    for title, desc, y in srv_items:
        b = FancyBboxPatch((12.4, y - 0.35), 4.6, 0.72, boxstyle="round,pad=0.06,rounding_size=0.08",
                           facecolor=BOX_FILL, edgecolor=BOX_BORDER, linewidth=1)
        ax.add_patch(b)
        ax.text(14.7, y + 0.1, title, ha="center", va="center", color=TEXT_MAIN, fontsize=8.5, fontweight="bold")
        ax.text(14.7, y - 0.16, desc, ha="center", va="center", color=TEXT_SUB, fontsize=7)

    # 5. CI/CD & REGISTRY TIER (Bottom Left)
    cicd_tier = FancyBboxPatch((0.8, 1.8), 10.9, 2.5, boxstyle="round,pad=0.12,rounding_size=0.15",
                               facecolor=BG_CICD, edgecolor=BORDER_CICD, linewidth=1.8)
    ax.add_patch(cicd_tier)
    ax.text(6.25, 3.9, "5. CI/CD & CONTAINER REGISTRY TIER",
            ha="center", va="center", color=BORDER_CICD, fontsize=11, fontweight="bold")

    cicd_sub = [
        ("GitHub Repository", "auto-mlops-aws-k8s\nSource control & branches", 2.6, 2.7),
        ("GitHub Actions CI", "Lint (flake8), Test (pytest)\nAutomated Multi-Stage Builds", 6.25, 2.7),
        ("Docker Hub Registry", "krishna250/mlops-serving\nkrishna250/mlops-training", 9.9, 2.7),
    ]
    for title, desc, x, y in cicd_sub:
        b = FancyBboxPatch((x - 1.6, y - 0.45), 3.2, 0.85, boxstyle="round,pad=0.06,rounding_size=0.08",
                           facecolor=BOX_FILL, edgecolor=BOX_BORDER, linewidth=1)
        ax.add_patch(b)
        ax.text(x, y + 0.15, title, ha="center", va="center", color=TEXT_MAIN, fontsize=8.5, fontweight="bold")
        lines = desc.split("\n")
        ax.text(x, y - 0.08, lines[0], ha="center", va="center", color=TEXT_SUB, fontsize=7)
        if len(lines) > 1:
            ax.text(x, y - 0.28, lines[1], ha="center", va="center", color=BORDER_CLIENT, fontsize=7)

    # Clean directional connectors
    # 1. UI -> NodePort
    a1 = FancyArrowPatch((4.0, 8.8), (4.8, 8.8), arrowstyle="-|>", color=BORDER_CLIENT, mutation_scale=14, linewidth=2)
    ax.add_patch(a1)
    ax.text(4.4, 9.1, "HTTP:30080", ha="center", va="center", color=BORDER_CLIENT, fontsize=7.5, fontweight="bold")

    # 2. Serving Pod -> S3 (Drift export)
    a2 = FancyArrowPatch((7.9, 7.2), (12.2, 8.9), arrowstyle="-|>", color=BORDER_STORAGE, mutation_scale=14, linewidth=1.8,
                         connectionstyle="arc3,rad=-0.12")
    ax.add_patch(a2)
    ax.text(10.1, 8.35, "Syncs Drifted CSV", ha="center", va="center", color=BORDER_STORAGE, fontsize=7.5, fontweight="bold")

    # 3. S3 -> Lambda (s3:ObjectCreated)
    a3 = FancyArrowPatch((14.7, 6.8), (14.7, 5.0), arrowstyle="-|>", color=BORDER_STORAGE, mutation_scale=14, linewidth=2)
    ax.add_patch(a3)
    ax.text(15.7, 5.9, "s3:ObjectCreated\n(Put Event)", ha="center", va="center", color=BORDER_STORAGE, fontsize=7.5, fontweight="bold")

    # 4. Lambda -> Training Job (Trigger)
    a4 = FancyArrowPatch((12.2, 4.6), (11.4, 6.6), arrowstyle="-|>", color=BORDER_SERVERLESS, mutation_scale=14, linewidth=1.8,
                         connectionstyle="arc3,rad=-0.12")
    ax.add_patch(a4)
    ax.text(11.4, 5.4, "Triggers Retraining", ha="center", va="center", color=BORDER_SERVERLESS, fontsize=7.5, fontweight="bold")

    # 5. Lambda -> SNS
    a5 = FancyArrowPatch((14.7, 4.2), (14.7, 4.0), arrowstyle="-|>", color=BORDER_SERVERLESS, mutation_scale=14, linewidth=2)
    ax.add_patch(a5)

    # 6. Docker Hub -> K8s
    a6 = FancyArrowPatch((9.9, 3.2), (8.5, 4.8), arrowstyle="-|>", color=BORDER_COMPUTE, mutation_scale=14, linewidth=1.8,
                         connectionstyle="arc3,rad=-0.12")
    ax.add_patch(a6)
    ax.text(8.8, 3.8, "Docker Pull Image", ha="center", va="center", color=BORDER_COMPUTE, fontsize=7.5, fontweight="bold")

    plt.tight_layout()
    png_path = os.path.join(OUTPUT_DIR, "system_architecture_clean.png")
    fig.savefig(png_path, dpi=300, facecolor="#ffffff")
    plt.close(fig)
    print(f"Generated clean architecture: {png_path}")

    # Copy to brain artifact directory as well
    import shutil
    shutil.copy(png_path, os.path.join(ARTIFACT_DIR, "system_architecture_clean.png"))
    print("Copied to artifact directory!")

if __name__ == "__main__":
    create_clean_architecture()
