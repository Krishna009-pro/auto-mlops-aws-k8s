"""
SentinelOps - Diagram Generation Script
Generates high-resolution PNG (300 DPI) and standalone SVG diagrams for the Cloud-Native MLOps project.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

OUTPUT_DIR = r"k:\Degree\Sem 5\Cloud-Native MLOps\Practicals\mlops-automated-pipeline\docs\diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# Color Palette (Modern Cloud / Tech aesthetic)
# -------------------------------------------------------------
NAVY_BG = "#0f172a"
CARD_BG = "#1e293b"
CARD_BORDER = "#334155"
TEXT_WHITE = "#f8fafc"
TEXT_MUTED = "#94a3b8"
ACCENT_GREEN = "#10b981"
ACCENT_BLUE = "#38bdf8"
ACCENT_ORANGE = "#f59e0b"
ACCENT_PURPLE = "#a855f7"
ACCENT_RED = "#ef4444"
AWS_COLOR = "#ff9900"
K8S_COLOR = "#326ce5"


def create_sequence_diagram():
    """Generates the Sequence Diagram (Lifelines and message interactions)."""
    fig, ax = plt.subplots(figsize=(18, 12), dpi=300)
    fig.patch.set_facecolor(NAVY_BG)
    ax.set_facecolor(NAVY_BG)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 13)
    ax.axis("off")

    # Title
    ax.text(9, 12.4, "SentinelOps: End-to-End MLOps Sequence Diagram", 
            ha="center", va="center", color=TEXT_WHITE, fontsize=18, fontweight="bold")
    ax.text(9, 12.0, "Real-time Explainable AI Inference, Statistical Drift Detection & Automated Cloud Retraining",
            ha="center", va="center", color=ACCENT_BLUE, fontsize=11)

    # Lifelines / Participants
    participants = [
        ("Client / UI\n(Browser)", 1.2, ACCENT_BLUE),
        ("FastAPI Serving\n(K3s Pod)", 3.4, K8S_COLOR),
        ("Inference & XAI\n(RandomForest)", 5.6, ACCENT_PURPLE),
        ("Drift Monitor\n(KS-Test)", 7.8, ACCENT_RED),
        ("AWS S3 Bucket\n(datasets/models)", 10.0, AWS_COLOR),
        ("AWS Lambda\n(MLOpsProcessor)", 12.2, AWS_COLOR),
        ("AWS SNS\n(mlops-alerts)", 14.4, ACCENT_GREEN),
        ("K8s Training Job\n(Batch Pod)", 16.6, K8S_COLOR),
    ]

    top_y = 11.2
    bottom_y = 0.8

    for name, x, color in participants:
        # Box header
        box = FancyBboxPatch((x - 0.95, top_y - 0.5), 1.9, 0.7,
                             boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=CARD_BG, edgecolor=color, linewidth=2, zorder=3)
        ax.add_patch(box)
        ax.text(x, top_y - 0.15, name, ha="center", va="center", color=TEXT_WHITE,
                fontsize=8.5, fontweight="bold", zorder=4)

        # Lifeline dashed vertical
        ax.plot([x, x], [bottom_y + 0.5, top_y - 0.5], color=CARD_BORDER,
                linestyle="--", linewidth=1.2, zorder=1)

        # Bottom box
        box_bot = FancyBboxPatch((x - 0.95, bottom_y - 0.2), 1.9, 0.45,
                                boxstyle="round,pad=0.1,rounding_size=0.15",
                                facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1, zorder=3)
        ax.add_patch(box_bot)
        ax.text(x, bottom_y + 0.02, name.split("\n")[0], ha="center", va="center", color=TEXT_MUTED,
                fontsize=7.5, zorder=4)

    # Sequence Messages
    steps = [
        # (from_idx, to_idx, y, label, color, dashed, note)
        (0, 1, 10.1, "1. POST /predict (Amount, Location, Device)", ACCENT_BLUE, False, None),
        (1, 2, 9.5, "2. Scale Features & Predict", TEXT_WHITE, False, None),
        (2, 1, 8.9, "3. Return Fraud Prob (88%) + XAI Factors", ACCENT_PURPLE, True, None),
        (1, 0, 8.3, "4. Render Result & XAI Factors in UI", ACCENT_BLUE, True, None),
        (1, 3, 7.7, "5. Stream Transaction to In-Memory Buffer", TEXT_MUTED, False, None),
        (3, 3, 7.1, "6. Kolmogorov-Smirnov Test (p-val < 0.05: Drift Detected)", ACCENT_RED, False, "self"),
        (3, 4, 6.4, "7. Export Drifted Dataset (s3://icem-mlops-krishna250/datasets/)", AWS_COLOR, False, None),
        (4, 5, 5.7, "8. S3 Event Notification (s3:ObjectCreated:Put)", AWS_COLOR, False, None),
        (5, 5, 5.1, "9. Validate Schema & Row Counts (242ms)", TEXT_WHITE, False, "self"),
        (5, 7, 4.4, "10. Trigger K8s Batch Training Job", K8S_COLOR, False, None),
        (7, 4, 3.7, "11. Upload model_v2.joblib & metrics.json", AWS_COLOR, False, None),
        (4, 5, 3.1, "12. Event: Evaluation Metrics Ready", AWS_COLOR, False, None),
        (5, 6, 2.5, "13. Quality Gate Passed (Acc >= 0.85) -> Publish Alert", ACCENT_GREEN, False, None),
        (6, 0, 1.9, "14. Email Notification dispatched to DevOps/Engineer", ACCENT_GREEN, True, None),
        (5, 1, 1.3, "15. Zero-Downtime Rolling Update (kubectl rollout restart)", ACCENT_ORANGE, False, None),
    ]

    for from_i, to_i, y, text, col, dashed, note in steps:
        x1 = participants[from_i][1]
        x2 = participants[to_i][1]
        ls = "--" if dashed else "-"

        if note == "self":
            # Loopback arrow on same participant
            loop_box = FancyBboxPatch((x1 - 0.1, y - 0.25), 1.8, 0.35,
                                      boxstyle="round,pad=0.05,rounding_size=0.1",
                                      facecolor="#261b36" if col == ACCENT_PURPLE else "#361b1b",
                                      edgecolor=col, linewidth=1, zorder=4)
            ax.add_patch(loop_box)
            ax.annotate("", xy=(x1, y - 0.25), xytext=(x1, y + 0.1),
                        arrowprops=dict(arrowstyle="->", color=col, lw=1.5,
                                        connectionstyle="arc3,rad=-0.5"))
            ax.text(x1 + 0.95, y - 0.08, text, ha="center", va="center", color=col,
                    fontsize=8, fontweight="bold", zorder=5)
        else:
            arrow = FancyArrowPatch((x1, y), (x2, y),
                                    arrowstyle="-|>",
                                    linestyle=ls,
                                    color=col,
                                    mutation_scale=12,
                                    linewidth=1.4,
                                    zorder=3)
            ax.add_patch(arrow)
            mid_x = (x1 + x2) / 2
            # Label background pill
            pill_w = len(text) * 0.105
            pill = FancyBboxPatch((mid_x - pill_w/2, y + 0.08), pill_w, 0.28,
                                  boxstyle="round,pad=0.04,rounding_size=0.08",
                                  facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=0.8, zorder=4)
            ax.add_patch(pill)
            ax.text(mid_x, y + 0.22, text, ha="center", va="center", color=col,
                    fontsize=8, fontweight="bold", zorder=5)

    plt.tight_layout()
    png_path = os.path.join(OUTPUT_DIR, "sequence_diagram.png")
    svg_path = os.path.join(OUTPUT_DIR, "sequence_diagram.svg")
    fig.savefig(png_path, dpi=300, facecolor=NAVY_BG)
    fig.savefig(svg_path, format="svg", facecolor=NAVY_BG)
    plt.close(fig)
    print(f"Generated: {png_path} and {svg_path}")


def create_system_architecture():
    """Generates the System Architecture Diagram."""
    fig, ax = plt.subplots(figsize=(19, 12), dpi=300)
    fig.patch.set_facecolor(NAVY_BG)
    ax.set_facecolor(NAVY_BG)
    ax.set_xlim(0, 19)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # Header
    ax.text(9.5, 11.4, "SentinelOps: Cloud-Native MLOps System Architecture",
            ha="center", va="center", color=TEXT_WHITE, fontsize=18, fontweight="bold")
    ax.text(9.5, 11.0, "End-to-End Infrastructure: AWS Cloud, Kubernetes (K3s), Event-Driven Serverless Pipeline & CI/CD",
            ha="center", va="center", color=ACCENT_BLUE, fontsize=11)

    # 1. Client Tier (Left)
    client_box = FancyBboxPatch((0.6, 6.0), 3.0, 4.3, boxstyle="round,pad=0.15,rounding_size=0.2",
                                facecolor=CARD_BG, edgecolor=ACCENT_BLUE, linewidth=1.8)
    ax.add_patch(client_box)
    ax.text(2.1, 9.9, "CLIENT TIER", ha="center", va="center", color=ACCENT_BLUE, fontsize=11, fontweight="bold")
    ax.text(2.1, 9.4, "User & Inference Interfaces", ha="center", va="center", color=TEXT_MUTED, fontsize=8)

    sub_items_client = [
        ("Web UI Dashboard", "SentinelOps Single Page App", 8.4),
        ("Explainable AI (XAI)", "Feature Impact & Risk Badges", 7.4),
        ("Live Audit Stream", "Dual-Layer LocalStorage Buffer", 6.4),
    ]
    for title, desc, y in sub_items_client:
        b = FancyBboxPatch((0.8, y - 0.35), 2.6, 0.7, boxstyle="round,pad=0.08,rounding_size=0.1",
                           facecolor="#0f172a", edgecolor=CARD_BORDER, linewidth=1)
        ax.add_patch(b)
        ax.text(2.1, y + 0.1, title, ha="center", va="center", color=TEXT_WHITE, fontsize=8.5, fontweight="bold")
        ax.text(2.1, y - 0.15, desc, ha="center", va="center", color=TEXT_MUTED, fontsize=7)

    # 2. Compute Tier (Kubernetes on AWS EC2) - Center
    k8s_box = FancyBboxPatch((4.2, 3.8), 7.0, 6.5, boxstyle="round,pad=0.15,rounding_size=0.2",
                             facecolor=CARD_BG, edgecolor=K8S_COLOR, linewidth=2.0)
    ax.add_patch(k8s_box)
    ax.text(7.7, 9.9, "COMPUTE TIER: AWS EC2 (t3.medium) + KUBERNETES (K3s)",
            ha="center", va="center", color=K8S_COLOR, fontsize=11, fontweight="bold")
    ax.text(7.7, 9.4, "NodePort 30080  |  Namespace: default / mlops  |  IAM Role: MLOpsEC2Role",
            ha="center", va="center", color=TEXT_MUTED, fontsize=8)

    # Ingress / NodePort
    np_box = FancyBboxPatch((4.6, 8.1), 6.2, 0.9, boxstyle="round,pad=0.08,rounding_size=0.1",
                            facecolor="#1e1e38", edgecolor=ACCENT_BLUE, linewidth=1.2)
    ax.add_patch(np_box)
    ax.text(7.7, 8.65, "Kubernetes Service: fraud-detector-service (NodePort 30080 -> 8000)",
            ha="center", va="center", color=TEXT_WHITE, fontsize=8.5, fontweight="bold")
    ax.text(7.7, 8.35, "TCP Traffic Routing & Load Balancing across Serving Pod Replicas",
            ha="center", va="center", color=ACCENT_BLUE, fontsize=7)

    # Serving Pods Deployment
    srv_pod = FancyBboxPatch((4.6, 5.8), 2.9, 2.0, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor="#0f172a", edgecolor=ACCENT_GREEN, linewidth=1.2)
    ax.add_patch(srv_pod)
    ax.text(6.05, 7.45, "Serving Pod (Deployment)", ha="center", va="center", color=ACCENT_GREEN, fontsize=8.5, fontweight="bold")
    ax.text(6.05, 7.1, "FastAPI Microservice (Uvicorn)", ha="center", va="center", color=TEXT_WHITE, fontsize=7.5)
    ax.text(6.05, 6.75, "RandomForest Classifier", ha="center", va="center", color=TEXT_MUTED, fontsize=7)
    ax.text(6.05, 6.4, "Health Probes: /health, /ready", ha="center", va="center", color=TEXT_MUTED, fontsize=7)
    ax.text(6.05, 6.05, "Drift Evaluator (KS-Test)", ha="center", va="center", color=ACCENT_ORANGE, fontsize=7, fontweight="bold")

    # Batch Training Job
    trn_pod = FancyBboxPatch((7.9, 5.8), 2.9, 2.0, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor="#0f172a", edgecolor=ACCENT_PURPLE, linewidth=1.2)
    ax.add_patch(trn_pod)
    ax.text(9.35, 7.45, "Training Job (Ephemeral Pod)", ha="center", va="center", color=ACCENT_PURPLE, fontsize=8.5, fontweight="bold")
    ax.text(9.35, 7.1, "Python 3.11 Scikit-Learn Engine", ha="center", va="center", color=TEXT_WHITE, fontsize=7.5)
    ax.text(9.35, 6.75, "Synthetic Drift Ingestion", ha="center", va="center", color=TEXT_MUTED, fontsize=7)
    ax.text(9.35, 6.4, "Quality Gatekeeper Evaluator", ha="center", va="center", color=TEXT_MUTED, fontsize=7)
    ax.text(9.35, 6.05, "Job Auto-Termination", ha="center", va="center", color=ACCENT_BLUE, fontsize=7)

    # ConfigMap & Volume Mounts
    cfg_box = FancyBboxPatch((4.6, 4.2), 6.2, 1.2, boxstyle="round,pad=0.08,rounding_size=0.1",
                             facecolor="#0f172a", edgecolor=CARD_BORDER, linewidth=1)
    ax.add_patch(cfg_box)
    ax.text(7.7, 5.1, "Cluster Config & IAM Integration", ha="center", va="center", color=TEXT_WHITE, fontsize=8, fontweight="bold")
    ax.text(7.7, 4.7, "ConfigMap (S3_BUCKET=icem-mlops-krishna250, AWS_DEFAULT_REGION=ap-south-1)", ha="center", va="center", color=TEXT_MUTED, fontsize=7)
    ax.text(7.7, 4.4, "IAM Instance Profile: MLOpsEC2Role (Least-Privilege S3, SNS, CloudWatch Policies)", ha="center", va="center", color=ACCENT_ORANGE, fontsize=7)

    # 3. AWS Cloud Storage & Model Registry (Right Upper)
    s3_box = FancyBboxPatch((11.8, 6.8), 3.3, 3.5, boxstyle="round,pad=0.15,rounding_size=0.2",
                            facecolor=CARD_BG, edgecolor=AWS_COLOR, linewidth=1.8)
    ax.add_patch(s3_box)
    ax.text(13.45, 9.9, "STORAGE & REGISTRY", ha="center", va="center", color=AWS_COLOR, fontsize=11, fontweight="bold")
    ax.text(13.45, 9.5, "AWS S3: icem-mlops-krishna250", ha="center", va="center", color=TEXT_MUTED, fontsize=7.5)

    s3_sub = [
        ("datasets/", "Raw & Drifted CSVs (v1, v2)", 8.7),
        ("models/", "Trained model.joblib weights", 7.9),
        ("metrics/", "summary_*.json performance logs", 7.1),
    ]
    for title, desc, y in s3_sub:
        b = FancyBboxPatch((12.0, y - 0.28), 2.9, 0.58, boxstyle="round,pad=0.06,rounding_size=0.08",
                           facecolor="#0f172a", edgecolor=CARD_BORDER, linewidth=1)
        ax.add_patch(b)
        ax.text(13.45, y + 0.08, title, ha="center", va="center", color=TEXT_WHITE, fontsize=8, fontweight="bold")
        ax.text(13.45, y - 0.12, desc, ha="center", va="center", color=TEXT_MUTED, fontsize=6.8)

    # 4. Serverless Event & Alerting Tier (Right Lower)
    srvless_box = FancyBboxPatch((11.8, 2.5), 3.3, 3.8, boxstyle="round,pad=0.15,rounding_size=0.2",
                                facecolor=CARD_BG, edgecolor=ACCENT_GREEN, linewidth=1.8)
    ax.add_patch(srvless_box)
    ax.text(13.45, 5.9, "SERVERLESS & ALERTS", ha="center", va="center", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    ax.text(13.45, 5.5, "Event-Driven Automation Core", ha="center", va="center", color=TEXT_MUTED, fontsize=7.5)

    srvless_sub = [
        ("AWS Lambda: MLOpsProcessor", "Validates schema & triggers CT (242ms)", 4.7, AWS_COLOR),
        ("AWS SNS: mlops-alerts", "Dispatches email to subscribers", 3.7, ACCENT_GREEN),
        ("Amazon CloudWatch", "Centralized metrics & execution logs", 2.8, ACCENT_BLUE),
    ]
    for title, desc, y, col in srvless_sub:
        b = FancyBboxPatch((12.0, y - 0.32), 2.9, 0.65, boxstyle="round,pad=0.06,rounding_size=0.08",
                           facecolor="#0f172a", edgecolor=CARD_BORDER, linewidth=1)
        ax.add_patch(b)
        ax.text(13.45, y + 0.1, title, ha="center", va="center", color=col, fontsize=7.8, fontweight="bold")
        ax.text(13.45, y - 0.14, desc, ha="center", va="center", color=TEXT_MUTED, fontsize=6.8)

    # 5. CI/CD & Registry (Bottom Left)
    cicd_box = FancyBboxPatch((0.6, 1.2), 10.6, 2.2, boxstyle="round,pad=0.15,rounding_size=0.2",
                              facecolor=CARD_BG, edgecolor=ACCENT_PURPLE, linewidth=1.5)
    ax.add_patch(cicd_box)
    ax.text(5.9, 3.0, "CONTINUOUS INTEGRATION & CONTAINER REGISTRY (CI/CD)",
            ha="center", va="center", color=ACCENT_PURPLE, fontsize=10.5, fontweight="bold")

    cicd_items = [
        ("GitHub Repository", "auto-mlops-aws-k8s\nSource control & branches", 2.0, 1.8),
        ("GitHub Actions CI", "Lint (flake8), Unit Test (pytest)\nDocker Multi-Stage Build", 5.9, 1.8),
        ("Docker Hub Registry", "krishna250/mlops-serving\nkrishna250/mlops-training", 9.6, 1.8),
    ]
    for title, desc, x, y in cicd_items:
        b = FancyBboxPatch((x - 1.6, y - 0.45), 3.2, 0.85, boxstyle="round,pad=0.06,rounding_size=0.08",
                           facecolor="#0f172a", edgecolor=CARD_BORDER, linewidth=1)
        ax.add_patch(b)
        ax.text(x, y + 0.15, title, ha="center", va="center", color=TEXT_WHITE, fontsize=8, fontweight="bold")
        lines = desc.split("\n")
        ax.text(x, y - 0.08, lines[0], ha="center", va="center", color=TEXT_MUTED, fontsize=6.8)
        if len(lines) > 1:
            ax.text(x, y - 0.28, lines[1], ha="center", va="center", color=ACCENT_BLUE, fontsize=6.8)

    # Connectors / Arrows between tiers
    # Client -> K8s
    a1 = FancyArrowPatch((3.6, 8.5), (4.6, 8.5), arrowstyle="-|>", color=ACCENT_BLUE, mutation_scale=14, linewidth=2)
    ax.add_patch(a1)
    ax.text(4.1, 8.8, "HTTP:30080", ha="center", va="center", color=ACCENT_BLUE, fontsize=7.5, fontweight="bold")

    # K8s Serving Pod -> S3 (Upload drifted data)
    a2 = FancyArrowPatch((7.5, 6.8), (11.8, 8.7), arrowstyle="-|>", color=AWS_COLOR, mutation_scale=14, linewidth=1.8,
                         connectionstyle="arc3,rad=-0.15")
    ax.add_patch(a2)
    ax.text(9.8, 8.2, "Syncs Drifted CSV", ha="center", va="center", color=AWS_COLOR, fontsize=7.5, fontweight="bold")

    # S3 -> Lambda (s3:ObjectCreated)
    a3 = FancyArrowPatch((13.45, 6.8), (13.45, 5.0), arrowstyle="-|>", color=AWS_COLOR, mutation_scale=14, linewidth=2)
    ax.add_patch(a3)
    ax.text(14.3, 5.9, "s3:ObjectCreated\n(Put Event)", ha="center", va="center", color=AWS_COLOR, fontsize=7.5, fontweight="bold")

    # Lambda -> SNS
    a4 = FancyArrowPatch((13.45, 4.3), (13.45, 4.0), arrowstyle="-|>", color=ACCENT_GREEN, mutation_scale=14, linewidth=2)
    ax.add_patch(a4)

    # SNS -> DevOps Alert (Arrow pointing out)
    a5 = FancyArrowPatch((15.1, 3.7), (17.5, 3.7), arrowstyle="-|>", color=ACCENT_GREEN, mutation_scale=14, linewidth=2)
    ax.add_patch(a5)
    ax.text(16.3, 4.1, "SNS Email / SMS\nNotifications", ha="center", va="center", color=ACCENT_GREEN, fontsize=7.5, fontweight="bold")

    # Lambda -> Training Job (Trigger)
    a6 = FancyArrowPatch((11.8, 4.7), (10.8, 6.5), arrowstyle="-|>", color=ACCENT_PURPLE, mutation_scale=14, linewidth=1.8,
                         connectionstyle="arc3,rad=-0.15")
    ax.add_patch(a6)
    ax.text(11.2, 5.4, "Triggers Retraining", ha="center", va="center", color=ACCENT_PURPLE, fontsize=7.5, fontweight="bold")

    # Docker Hub -> K8s (Pull Images)
    a7 = FancyArrowPatch((9.6, 2.3), (8.5, 3.8), arrowstyle="-|>", color=K8S_COLOR, mutation_scale=14, linewidth=1.8,
                         connectionstyle="arc3,rad=-0.15")
    ax.add_patch(a7)
    ax.text(8.7, 2.9, "Docker Pull Image", ha="center", va="center", color=K8S_COLOR, fontsize=7.5, fontweight="bold")

    plt.tight_layout()
    png_path = os.path.join(OUTPUT_DIR, "system_architecture.png")
    svg_path = os.path.join(OUTPUT_DIR, "system_architecture.svg")
    fig.savefig(png_path, dpi=300, facecolor=NAVY_BG)
    fig.savefig(svg_path, format="svg", facecolor=NAVY_BG)
    plt.close(fig)
    print(f"Generated: {png_path} and {svg_path}")


def create_mlops_pipeline_flow():
    """Generates the MLOps Continuous Training (CT) Pipeline Workflow."""
    fig, ax = plt.subplots(figsize=(19, 10), dpi=300)
    fig.patch.set_facecolor(NAVY_BG)
    ax.set_facecolor(NAVY_BG)
    ax.set_xlim(0, 19)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(9.5, 9.4, "SentinelOps: Closed-Loop Continuous Training (CT) Pipeline",
            ha="center", va="center", color=TEXT_WHITE, fontsize=18, fontweight="bold")
    ax.text(9.5, 9.0, "Automated 6-Stage Lifecycle from Drift Detection to Zero-Downtime Deployment",
            ha="center", va="center", color=ACCENT_GREEN, fontsize=11)

    stages = [
        ("STAGE 1", "Data Ingestion &\nDrift Detection", 
         "• KS-Test monitoring\n• p-value < 0.05 threshold\n• Drifted dataset export", ACCENT_BLUE, 2.0),
        ("STAGE 2", "Event Trigger &\nValidation", 
         "• S3:ObjectCreated Put\n• AWS Lambda schema check\n• Row count & type validation", AWS_COLOR, 5.0),
        ("STAGE 3", "Distributed Model\nRetraining", 
         "• Ephemeral K8s Job\n• RandomForestClassifier\n• Hyperparameter fitting", K8S_COLOR, 8.0),
        ("STAGE 4", "Model Evaluation &\nQuality Gate", 
         "• Accuracy >= 85% check\n• F1-Score & ROC-AUC\n• Metric summary artifact", ACCENT_PURPLE, 11.0),
        ("STAGE 5", "Artifact Registry\nVersioning", 
         "• S3 models/ storage\n• Timestamped weights\n• Evaluation metrics JSON", ACCENT_ORANGE, 14.0),
        ("STAGE 6", "Zero-Downtime\nDeployment", 
         "• kubectl rollout restart\n• Hot-swap model weights\n• SNS alert dispatched", ACCENT_GREEN, 17.0),
    ]

    card_y = 5.2
    card_h = 3.2
    card_w = 2.5

    for idx, (stage_num, title, bullets, col, x) in enumerate(stages):
        # Card outer
        card = FancyBboxPatch((x - card_w/2, card_y - card_h/2), card_w, card_h,
                              boxstyle="round,pad=0.1,rounding_size=0.15",
                              facecolor=CARD_BG, edgecolor=col, linewidth=1.8, zorder=2)
        ax.add_patch(card)

        # Stage badge
        badge = FancyBboxPatch((x - 0.75, card_y + card_h/2 - 0.35), 1.5, 0.45,
                               boxstyle="round,pad=0.05,rounding_size=0.1",
                               facecolor=col, edgecolor="none", zorder=3)
        ax.add_patch(badge)
        ax.text(x, card_y + card_h/2 - 0.12, stage_num, ha="center", va="center",
                color="#0f172a", fontsize=8, fontweight="bold", zorder=4)

        # Card Title
        ax.text(x, card_y + 0.6, title, ha="center", va="center",
                color=TEXT_WHITE, fontsize=9.5, fontweight="bold", zorder=3)

        # Bullet points
        ax.text(x - card_w/2 + 0.25, card_y - 0.6, bullets, ha="left", va="center",
                color=TEXT_MUTED, fontsize=7.5, linespacing=1.6, zorder=3)

        # Forward Arrow to next stage
        if idx < len(stages) - 1:
            next_x = stages[idx + 1][4]
            arr = FancyArrowPatch((x + card_w/2 + 0.05, card_y), (next_x - card_w/2 - 0.05, card_y),
                                  arrowstyle="-|>", color=TEXT_WHITE, mutation_scale=14, linewidth=2, zorder=5)
            ax.add_patch(arr)

    # Feedback Loop (Bottom Arrow from Stage 6 back to Stage 1)
    loop_y = 1.8
    loop_arr = FancyArrowPatch((17.0, card_y - card_h/2 - 0.1), (2.0, card_y - card_h/2 - 0.1),
                               arrowstyle="-|>", color=ACCENT_GREEN, mutation_scale=16, linewidth=2.2,
                               connectionstyle="arc3,rad=-0.18", linestyle="--", zorder=5)
    ax.add_patch(loop_arr)
    
    # Feedback loop label pill
    fb_pill = FancyBboxPatch((9.5 - 2.8, loop_y - 0.3), 5.6, 0.6,
                             boxstyle="round,pad=0.08,rounding_size=0.15",
                             facecolor="#132e22", edgecolor=ACCENT_GREEN, linewidth=1.2, zorder=6)
    ax.add_patch(fb_pill)
    ax.text(9.5, loop_y, "CONTINUOUS MONITORING & RETRAINING FEEDBACK LOOP",
            ha="center", va="center", color=ACCENT_GREEN, fontsize=8.5, fontweight="bold", zorder=7)

    plt.tight_layout()
    png_path = os.path.join(OUTPUT_DIR, "mlops_pipeline_flow.png")
    svg_path = os.path.join(OUTPUT_DIR, "mlops_pipeline_flow.svg")
    fig.savefig(png_path, dpi=300, facecolor=NAVY_BG)
    fig.savefig(svg_path, format="svg", facecolor=NAVY_BG)
    plt.close(fig)
    print(f"Generated: {png_path} and {svg_path}")


def create_k8s_topology():
    """Generates the Kubernetes Cluster & AWS Network Topology Diagram."""
    fig, ax = plt.subplots(figsize=(18, 11), dpi=300)
    fig.patch.set_facecolor(NAVY_BG)
    ax.set_facecolor(NAVY_BG)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 11)
    ax.axis("off")

    # Title
    ax.text(9, 10.4, "SentinelOps: Kubernetes (K3s) Cluster & Network Topology",
            ha="center", va="center", color=TEXT_WHITE, fontsize=18, fontweight="bold")
    ax.text(9, 10.0, "Microservices Orchestration, NodePort Ingress, Health Probes & S3 Integration",
            ha="center", va="center", color=K8S_COLOR, fontsize=11)

    # EC2 Instance Boundary
    ec2_box = FancyBboxPatch((1.0, 1.2), 16.0, 8.2, boxstyle="round,pad=0.2,rounding_size=0.25",
                             facecolor="#131c2e", edgecolor="#2563eb", linewidth=2.0)
    ax.add_patch(ec2_box)
    ax.text(2.8, 9.0, "AWS EC2: mlops-k3s-server", ha="left", va="center", color="#93c5fd", fontsize=11, fontweight="bold")
    ax.text(2.8, 8.6, "Instance: t3.medium (2 vCPU, 4GB RAM)  |  OS: Ubuntu 24.04 LTS  |  Security Group: Ports 22, 8000, 30080",
            ha="left", va="center", color=TEXT_MUTED, fontsize=8)

    # Ingress / NodePort Box
    nodeport = FancyBboxPatch((1.6, 5.0), 3.0, 2.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                              facecolor=CARD_BG, edgecolor=ACCENT_BLUE, linewidth=1.5)
    ax.add_patch(nodeport)
    ax.text(3.1, 7.3, "EXTERNAL INGRESS", ha="center", va="center", color=ACCENT_BLUE, fontsize=9.5, fontweight="bold")
    ax.text(3.1, 6.7, "NodePort: 30080", ha="center", va="center", color=TEXT_WHITE, fontsize=9, fontweight="bold")
    ax.text(3.1, 6.2, "Mapped to Direct Port 8000\nExternal HTTP traffic\nrouted into K8s cluster",
            ha="center", va="center", color=TEXT_MUTED, fontsize=7.5)

    # Kubernetes Service
    svc_box = FancyBboxPatch((5.4, 5.0), 3.4, 2.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=CARD_BG, edgecolor=K8S_COLOR, linewidth=1.5)
    ax.add_patch(svc_box)
    ax.text(7.1, 7.3, "K8S SERVICE", ha="center", va="center", color=K8S_COLOR, fontsize=9.5, fontweight="bold")
    ax.text(7.1, 6.7, "fraud-detector-service", ha="center", va="center", color=TEXT_WHITE, fontsize=8.5, fontweight="bold")
    ax.text(7.1, 6.1, "Type: NodePort\nSelector: app=fraud-detector\nInternal Cluster IP proxy\nLoad Balancer",
            ha="center", va="center", color=TEXT_MUTED, fontsize=7.5)

    # Serving Pods Deployment
    deploy_box = FancyBboxPatch((9.6, 4.6), 4.2, 3.6, boxstyle="round,pad=0.1,rounding_size=0.15",
                                facecolor=CARD_BG, edgecolor=ACCENT_GREEN, linewidth=1.5)
    ax.add_patch(deploy_box)
    ax.text(11.7, 7.8, "DEPLOYMENT: fraud-detector", ha="center", va="center", color=ACCENT_GREEN, fontsize=9.5, fontweight="bold")
    ax.text(11.7, 7.3, "Replicas: 1 (Scale-ready)  |  Strategy: RollingUpdate", ha="center", va="center", color=TEXT_MUTED, fontsize=7.5)

    # Container 1 inside Pod
    c1 = FancyBboxPatch((9.9, 5.0), 3.6, 1.9, boxstyle="round,pad=0.08,rounding_size=0.1",
                        facecolor="#0f172a", edgecolor=CARD_BORDER, linewidth=1)
    ax.add_patch(c1)
    ax.text(11.7, 6.55, "Container: mlops-serving", ha="center", va="center", color=TEXT_WHITE, fontsize=8.5, fontweight="bold")
    ax.text(11.7, 6.2, "Image: krishna250/mlops-serving:latest", ha="center", va="center", color=ACCENT_BLUE, fontsize=7)
    ax.text(11.7, 5.8, "• Liveness Probe: /health (HTTP 8000)\n• Readiness Probe: /health (initialDelay: 5s)\n• Resources: 250m CPU, 512Mi Memory",
            ha="center", va="center", color=TEXT_MUTED, fontsize=6.8)

    # Batch Training Pod (Bottom right)
    job_box = FancyBboxPatch((9.6, 1.8), 4.2, 2.2, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=CARD_BG, edgecolor=ACCENT_PURPLE, linewidth=1.5)
    ax.add_patch(job_box)
    ax.text(11.7, 3.6, "BATCH JOB: fraud-trainer", ha="center", va="center", color=ACCENT_PURPLE, fontsize=9.5, fontweight="bold")
    ax.text(11.7, 3.1, "Image: krishna250/mlops-training:latest", ha="center", va="center", color=TEXT_WHITE, fontsize=7.5)
    ax.text(11.7, 2.5, "Ephemeral pod • Pulls dataset • Trains RandomForest • Syncs S3 • Terminated (Exit 0)",
            ha="center", va="center", color=TEXT_MUTED, fontsize=7)

    # Volume & ConfigMap
    cfg_vol = FancyBboxPatch((1.6, 1.8), 7.2, 2.2, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=CARD_BG, edgecolor=ACCENT_ORANGE, linewidth=1.2)
    ax.add_patch(cfg_vol)
    ax.text(5.2, 3.6, "CONFIG & PERSISTENCE LAYER", ha="center", va="center", color=ACCENT_ORANGE, fontsize=9.5, fontweight="bold")
    ax.text(5.2, 3.0, "ConfigMap: mlops-config (S3_BUCKET, AWS_DEFAULT_REGION, PORT=8000)", ha="center", va="center", color=TEXT_WHITE, fontsize=7.5)
    ax.text(5.2, 2.4, "Volume Mount: /app/artifacts/ (Mounted to datasets, models, metrics on local disk / S3 sync)",
            ha="center", va="center", color=TEXT_MUTED, fontsize=7)

    # AWS Cloud (Right Side Outside EC2)
    aws_cloud = FancyBboxPatch((14.4, 2.5), 2.2, 5.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                               facecolor="#261b0c", edgecolor=AWS_COLOR, linewidth=1.8)
    ax.add_patch(aws_cloud)
    ax.text(15.5, 7.8, "AWS CLOUD", ha="center", va="center", color=AWS_COLOR, fontsize=10, fontweight="bold")
    ax.text(15.5, 7.0, "S3 Bucket\nicem-mlops-krishna250", ha="center", va="center", color=TEXT_WHITE, fontsize=7.5)
    ax.text(15.5, 5.6, "AWS Lambda\nMLOpsProcessor", ha="center", va="center", color=TEXT_WHITE, fontsize=7.5)
    ax.text(15.5, 4.2, "AWS SNS\nmlops-alerts", ha="center", va="center", color=TEXT_WHITE, fontsize=7.5)
    ax.text(15.5, 3.0, "IAM Role\nMLOpsEC2Role", ha="center", va="center", color=ACCENT_ORANGE, fontsize=7.5)

    # Connectors
    arr1 = FancyArrowPatch((4.6, 6.4), (5.4, 6.4), arrowstyle="-|>", color=ACCENT_BLUE, mutation_scale=14, linewidth=2)
    ax.add_patch(arr1)

    arr2 = FancyArrowPatch((8.8, 6.4), (9.6, 6.4), arrowstyle="-|>", color=K8S_COLOR, mutation_scale=14, linewidth=2)
    ax.add_patch(arr2)

    arr3 = FancyArrowPatch((13.8, 6.4), (14.4, 6.4), arrowstyle="<|-|>", color=AWS_COLOR, mutation_scale=14, linewidth=1.8)
    ax.add_patch(arr3)

    plt.tight_layout()
    png_path = os.path.join(OUTPUT_DIR, "k8s_deployment_topology.png")
    svg_path = os.path.join(OUTPUT_DIR, "k8s_deployment_topology.svg")
    fig.savefig(png_path, dpi=300, facecolor=NAVY_BG)
    fig.savefig(svg_path, format="svg", facecolor=NAVY_BG)
    plt.close(fig)
    print(f"Generated: {png_path} and {svg_path}")


if __name__ == "__main__":
    create_sequence_diagram()
    create_system_architecture()
    create_mlops_pipeline_flow()
    create_k8s_topology()
    print("All diagrams generated successfully!")
