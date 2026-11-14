# PowerShell script to deploy MLOps components to Kubernetes (EKS / K3s / Minikube)
param (
    [string]$Namespace = "mlops",
    [string]$DockerUser = "yourdockerhub"
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Deploying MLOps to Kubernetes: $Namespace" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Apply Namespace
Write-Host "`n[1/5] Applying Namespace..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml

# 2. Apply ConfigMap
Write-Host "`n[2/5] Applying ConfigMap..." -ForegroundColor Yellow
kubectl apply -f k8s/configmap.yaml

# 3. Apply ServiceAccount (IRSA)
Write-Host "`n[3/5] Applying ServiceAccount..." -ForegroundColor Yellow
kubectl apply -f k8s/serviceaccount-irsa.yaml

# 4. Apply Deployment (Serving API)
Write-Host "`n[4/5] Applying Deployment..." -ForegroundColor Yellow
kubectl apply -f k8s/deployment.yaml

# 5. Apply Service (Exposing endpoint)
Write-Host "`n[5/5] Applying Service..." -ForegroundColor Yellow
kubectl apply -f k8s/service.yaml

Write-Host "`n[INFO] Checking Pod rollout status..." -ForegroundColor Cyan
kubectl rollout status deployment/mlops-serving-api -n $Namespace

Write-Host "`n[SUCCESS] Kubernetes Deployment Complete!" -ForegroundColor Green
Write-Host "Run the following to inspect resources:"
Write-Host "  kubectl get pods,svc -n $Namespace -o wide"
