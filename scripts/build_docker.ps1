# PowerShell script to build and tag Docker images for MLOps pipeline
param (
    [string]$DockerUser = "krishna250",
    [string]$Tag = "latest"
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Building MLOps Docker Images: $DockerUser" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Build Trainer Image
Write-Host "`n[1/2] Building Trainer Image: $DockerUser/mlops-trainer:$Tag..." -ForegroundColor Yellow
docker build -t "$DockerUser/mlops-trainer:$Tag" src/train
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to build Trainer Docker image!" -ForegroundColor Red
    exit 1
}

# 2. Build Serving API Image
Write-Host "`n[2/2] Building Serving API Image: $DockerUser/mlops-serving:$Tag..." -ForegroundColor Yellow
docker build -t "$DockerUser/mlops-serving:$Tag" src/serve
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to build Serving Docker image!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[SUCCESS] Both Docker images built successfully!" -ForegroundColor Green
Write-Host "To push to Docker Hub, run:" -ForegroundColor Cyan
Write-Host "  docker login"
Write-Host "  docker push $DockerUser/mlops-trainer:$Tag"
Write-Host "  docker push $DockerUser/mlops-serving:$Tag"

