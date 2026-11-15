"""
SentinelOps - Architecture Diagram Rendered in Exact Mermaid Dark Theme Style
Matches the sleek dark card (#18181b), rounded dark pills (#27272a), crisp white typography,
and clean directional connectors of Mermaid diagrams.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUTPUT_DIR = r"k:\Degree\Sem 5\Cloud-Native MLOps\Practicals\mlops-automated-pipeline\docs\diagrams"
ARTIFACT_DIR = r"C:\Users\kkp18\.gemini\antigravity\brain\b79467d7-9886-423e-abc5-5fa34156e482"

def render_mermaid_dark_architecture():
    fig, ax = plt.subplots(figsize=(19, 13), dpi=300)
    
    # Exact Mermaid Dark Colors from user screenshot
    BG_DARK = "#18181b"          # Tailwind zinc-900 / dark card
    CONTAINER_BORDER = "#27272a"
    SUBGRAPH_BG = "#202024"       # Slightly lighter subgraph background
    SUBGRAPH_BORDER = "#3f3f46"
    NODE_BG = "#27272a"          # Node pill fill
    NODE_BORDER = "#52525b"      # Node pill border
    TEXT_WHITE = "#f4f4f5"
    TEXT_MUTED = "#a1a1aa"
    LINE_COLOR = "#a1a1aa"
    LABEL_BG = "#27272a"

    fig.patch.set_facecolor(BG_DARK)
    ax.set_facecolor(BG_DARK)
    ax.set_xlim(0, 19)
    ax.set_ylim(0, 13)
    ax.axis("off")

    # Title
    ax.text(9.5, 12.3, "SentinelOps: Cloud-Native System Architecture (Mermaid Edition)",
            ha="center", va="center", color=TEXT_WHITE, fontsize=17, fontweight="bold")
    ax.text(9.5, 11.9, "Clean Decoupled Flowchart: Ingestion, Compute, Storage, Serverless & CI/CD",
            ha="center", va="center", color=TEXT_MUTED, fontsize=10.5)

    # 1. CLIENT TIER (Top Left)
    sub1 = FancyBboxPatch((0.8, 6.4), 3.4, 4.8, boxstyle="round,pad=0.12,rounding_size=0.15",
                          facecolor=SUBGRAPH_BG, edgecolor=SUBGRAPH_BORDER, linewidth=1.2)
    ax.add_patch(sub1)
    ax.text(2.5, 10.7, "1. CLIENT TIER (User & Interface)",
            ha="center", va="center", color=TEXT_WHITE, fontsize=10, fontweight="bold")

    client_nodes = [
        ("Web UI Dashboard (SentinelOps)", 9.7),
        ("Explainable AI Panel (Risk Indicators)", 8.4),
        ("Live Transaction Audit Stream", 7.1),
    ]
    for text, y in client_nodes:
        b = FancyBboxPatch((1.1, y - 0.42), 2.8, 0.84, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor=NODE_BG, edgecolor=NODE_BORDER, linewidth=1.2)
        ax.add_patch(b)
        ax.text(2.5, y, text, ha="center", va="center", color=TEXT_WHITE, fontsize=8.2, fontweight="600")

    # 2. COMPUTE TIER (Top Center)
    sub2 = FancyBboxPatch((4.7, 4.8), 7.6, 6.4, boxstyle="round,pad=0.12,rounding_size=0.15",
                          facecolor=SUBGRAPH_BG, edgecolor=SUBGRAPH_BORDER, linewidth=1.2)
    ax.add_patch(sub2)
    ax.text(8.5, 10.7, "2. COMPUTE TIER (AWS EC2 + Kubernetes K3s)",
            ha="center", va="center", color=TEXT_WHITE, fontsize=10, fontweight="bold")

    # NodePort
    b_np = FancyBboxPatch((5.1, 9.3), 6.8, 0.82, boxstyle="round,pad=0.08,rounding_size=0.12",
                          facecolor=NODE_BG, edgecolor=NODE_BORDER, linewidth=1.2)
    ax.add_patch(b_np)
    ax.text(8.5, 9.71, "Kubernetes NodePort (30080 -> 8000)", ha="center", va="center", color=TEXT_WHITE, fontsize=8.5, fontweight="600")

    # K8s Service
    b_svc = FancyBboxPatch((5.1, 8.1), 6.8, 0.82, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor=NODE_BG, edgecolor=NODE_BORDER, linewidth=1.2)
    ax.add_patch(b_svc)
    ax.text(8.5, 8.51, "K8s Service: fraud-detector-service", ha="center", va="center", color=TEXT_WHITE, fontsize=8.5, fontweight="600")

    # Serving Pod & Training Pod
    b_sp = FancyBboxPatch((5.1, 6.4), 3.2, 1.3, boxstyle="round,pad=0.08,rounding_size=0.12",
                          facecolor=NODE_BG, edgecolor="#10b981", linewidth=1.4)
    ax.add_patch(b_sp)
    ax.text(6.7, 7.2, "Serving Pod (Deployment)", ha="center", va="center", color="#34d399", fontsize=8.5, fontweight="bold")
    ax.text(6.7, 6.75, "FastAPI + RandomForest\n+ KS-Test Drift Monitor", ha="center", va="center", color=TEXT_WHITE, fontsize=7.2)

    b_tp = FancyBboxPatch((8.7, 6.4), 3.2, 1.3, boxstyle="round,pad=0.08,rounding_size=0.12",
                          facecolor=NODE_BG, edgecolor="#a855f7", linewidth=1.4)
    ax.add_patch(b_tp)
    ax.text(10.3, 7.2, "Training Job (Ephemeral Pod)", ha="center", va="center", color="#c084fc", fontsize=8.5, fontweight="bold")
    ax.text(10.3, 6.75, "Scikit-Learn Batch Job\nAuto-Terminates on Exit (0)", ha="center", va="center", color=TEXT_WHITE, fontsize=7.2)

    # ConfigMap
    b_cfg = FancyBboxPatch((5.1, 5.1), 6.8, 0.9, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor=NODE_BG, edgecolor=NODE_BORDER, linewidth=1.2)
    ax.add_patch(b_cfg)
    ax.text(8.5, 5.55, "ConfigMap & IAM Role: MLOpsEC2Role", ha="center", va="center", color=TEXT_WHITE, fontsize=8.5, fontweight="600")

    # 3. STORAGE & REGISTRY (Top Right)
    sub3 = FancyBboxPatch((12.8, 7.2), 5.4, 4.0, boxstyle="round,pad=0.12,rounding_size=0.15",
                          facecolor=SUBGRAPH_BG, edgecolor=SUBGRAPH_BORDER, linewidth=1.2)
    ax.add_patch(sub3)
    ax.text(15.5, 10.7, "3. STORAGE & REGISTRY (AWS S3)",
            ha="center", va="center", color="#fbbf24", fontsize=10, fontweight="bold")

    s3_items = [
        ("datasets/ (transactions_v1.csv, v2.csv)", 9.7),
        ("models/ (model.joblib, model_v2.joblib)", 8.5),
        ("metrics/ (summary_*.json performance)", 7.4),
    ]
    for text, y in s3_items:
        b = FancyBboxPatch((13.1, y - 0.38), 4.8, 0.76, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor=NODE_BG, edgecolor=NODE_BORDER, linewidth=1.2)
        ax.add_patch(b)
        ax.text(15.5, y, text, ha="center", va="center", color=TEXT_WHITE, fontsize=8, fontweight="600")

    # 4. SERVERLESS & MONITORING (Bottom Right)
    sub4 = FancyBboxPatch((12.8, 1.8), 5.4, 4.9, boxstyle="round,pad=0.12,rounding_size=0.15",
                          facecolor=SUBGRAPH_BG, edgecolor=SUBGRAPH_BORDER, linewidth=1.2)
    ax.add_patch(sub4)
    ax.text(15.5, 6.2, "4. SERVERLESS & MONITORING (AWS Cloud)",
            ha="center", va="center", color="#c084fc", fontsize=10, fontweight="bold")

    srv_items = [
        ("AWS Lambda: MLOpsProcessor (242ms)", 5.2),
        ("AWS SNS Topic: mlops-alerts", 4.0),
        ("Amazon CloudWatch (Logs & Metrics)", 2.8),
    ]
    for text, y in srv_items:
        b = FancyBboxPatch((13.1, y - 0.38), 4.8, 0.76, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor=NODE_BG, edgecolor=NODE_BORDER, linewidth=1.2)
        ax.add_patch(b)
        ax.text(15.5, y, text, ha="center", va="center", color=TEXT_WHITE, fontsize=8, fontweight="600")

    # 5. CI/CD & REGISTRY TIER (Bottom Left)
    sub5 = FancyBboxPatch((0.8, 1.8), 11.5, 2.5, boxstyle="round,pad=0.12,rounding_size=0.15",
                          facecolor=SUBGRAPH_BG, edgecolor=SUBGRAPH_BORDER, linewidth=1.2)
    ax.add_patch(sub5)
    ax.text(6.55, 3.9, "5. CI/CD & REGISTRY TIER",
            ha="center", va="center", color=TEXT_WHITE, fontsize=10, fontweight="bold")

    cicd_items = [
        ("GitHub: auto-mlops-aws-k8s", 2.6, 2.7),
        ("GitHub Actions (Lint, Test, Docker Build)", 6.55, 2.7),
        ("Docker Hub: krishna250/mlops-serving & training", 10.3, 2.7),
    ]
    for text, x, y in cicd_items:
        b = FancyBboxPatch((x - 1.65, y - 0.42), 3.3, 0.84, boxstyle="round,pad=0.08,rounding_size=0.12",
                           facecolor=NODE_BG, edgecolor=NODE_BORDER, linewidth=1.2)
        ax.add_patch(b)
        ax.text(x, y, text, ha="center", va="center", color=TEXT_WHITE, fontsize=7.6, fontweight="600")

    # Connectors & Arrows (Exact Mermaid Flow)
    def draw_arrow(p1, p2, text=None, text_offset=(0, 0.25)):
        arr = FancyArrowPatch(p1, p2, arrowstyle="-|>", color=LINE_COLOR,
                              mutation_scale=14, linewidth=1.6, zorder=4)
        ax.add_patch(arr)
        if text:
            mx = (p1[0] + p2[0]) / 2 + text_offset[0]
            my = (p1[1] + p2[1]) / 2 + text_offset[1]
            pill_w = len(text) * 0.115
            pill = FancyBboxPatch((mx - pill_w/2, my - 0.16), pill_w, 0.32,
                                  boxstyle="round,pad=0.04,rounding_size=0.06",
                                  facecolor=LABEL_BG, edgecolor=SUBGRAPH_BORDER, linewidth=0.8, zorder=5)
            ax.add_patch(pill)
            ax.text(mx, my, text, ha="center", va="center", color=TEXT_MUTED, fontsize=7.2, fontweight="600", zorder=6)

    # 1. UI -> NodePort
    draw_arrow((3.9, 9.7), (5.1, 9.7), "HTTP POST :30080")
    # 2. NodePort -> Service
    draw_arrow((8.5, 9.3), (8.5, 8.92))
    # 3. Service -> Serving Pod
    draw_arrow((8.5, 8.1), (6.7, 7.7))
    # 4. Serving Pod -> S3
    draw_arrow((8.3, 7.3), (13.1, 8.8), "Syncs Drifted CSV", (0, 0.2))
    # 5. S3 -> Lambda
    draw_arrow((15.5, 7.2), (15.5, 5.6), "s3:ObjectCreated Put", (0.8, 0))
    # 6. Lambda -> Training Pod
    draw_arrow((13.1, 5.2), (11.9, 6.8), "Triggers Retraining Job", (-0.1, 0.2))
    # 7. Training Pod -> S3 Models
    draw_arrow((11.9, 7.3), (13.1, 8.4), "Uploads Model & Metrics", (0, -0.2))
    # 8. Lambda -> SNS
    draw_arrow((15.5, 4.8), (15.5, 4.4))
    # 9. Lambda -> Serving Pod (Rollout)
    draw_arrow((13.1, 4.7), (7.5, 6.4), "Rollout Restart", (-1.2, -0.2))
    # 10. Docker Hub -> Serving Pod
    draw_arrow((10.3, 3.12), (8.5, 5.1), "Pulls Container Image", (0.2, -0.2))

    plt.tight_layout()
    png_path = os.path.join(OUTPUT_DIR, "system_architecture_mermaid_exact.png")
    fig.savefig(png_path, dpi=300, facecolor=BG_DARK)
    plt.close(fig)
    print(f"Generated: {png_path}")

    # Copy to brain artifact directory as well
    import shutil
    shutil.copy(png_path, os.path.join(ARTIFACT_DIR, "system_architecture_mermaid_exact.png"))
    print("Copied to artifact directory!")

if __name__ == "__main__":
    render_mermaid_dark_architecture()
