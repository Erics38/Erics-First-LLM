# Tobi's Restaurant - One-Click Startup Script
# Run this to start the entire restaurant app

Write-Host "Starting Tobi's Restaurant..." -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectPath

Write-Host "Working in: $projectPath" -ForegroundColor Yellow

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Green
try {
    docker version | Out-Null
} catch {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Stop any existing containers on port 8000
Write-Host "Stopping any existing containers..." -ForegroundColor Yellow
$existingContainers = docker ps -q --filter "publish=8000"
if ($existingContainers) {
    docker stop $existingContainers | Out-Null
    docker rm $existingContainers | Out-Null
    Write-Host "SUCCESS: Cleaned up existing containers" -ForegroundColor Green
}

# Build the latest image
Write-Host "Building Tobi's Restaurant API..." -ForegroundColor Green
docker build -t tobi-restaurant . --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed. Check your code for errors." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start the container
Write-Host "Starting Tobi's API container..." -ForegroundColor Green
$containerName = "tobi-api-$(Get-Date -Format 'MMdd-HHmm')"
docker run -d --name $containerName -v "${PWD}/models:/app/models" -p 8000:8000 tobi-restaurant | Out-Null

# Wait for the API to be ready
Write-Host "Waiting for Tobi to wake up..." -ForegroundColor Yellow
$maxWait = 30
$waited = 0
$apiReady = $false

while ($waited -lt $maxWait -and -not $apiReady) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET -TimeoutSec 2
        if ($response.status -like "*running*") {
            $apiReady = $true
        }
    } catch {
        Start-Sleep -Seconds 2
        $waited += 2
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }
}

if ($apiReady) {
    Write-Host ""
    Write-Host "SUCCESS: Tobi's API is ready!" -ForegroundColor Green
    
    # Open the chat interface
    Write-Host "Opening Tobi's chat interface..." -ForegroundColor Green
    Start-Process "restaurant_chat.html"
    
    Write-Host ""
    Write-Host "TOBI'S RESTAURANT IS NOW RUNNING!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Chat Interface: Opened in your browser" -ForegroundColor White
    Write-Host "API Status: http://localhost:8000" -ForegroundColor White
    Write-Host "Menu Data: http://localhost:8000/menu" -ForegroundColor White
    Write-Host "Container: $containerName" -ForegroundColor White
    Write-Host ""
    Write-Host "TO SHARE WITH OTHERS:" -ForegroundColor Yellow
    Write-Host "   1. Install ngrok: https://ngrok.com" -ForegroundColor Gray
    Write-Host "   2. Run: ngrok http 8000" -ForegroundColor Gray
    Write-Host "   3. Share the https://xxx.ngrok.io URL" -ForegroundColor Gray
    Write-Host ""
    Write-Host "TO STOP: Press Ctrl+C or run: docker stop $containerName" -ForegroundColor Red
    Write-Host ""
    
    # Keep the script running and show logs
    Write-Host "Container logs (Press Ctrl+C to stop):" -ForegroundColor Cyan
    docker logs -f $containerName
    
} else {
    Write-Host ""
    Write-Host "ERROR: Tobi failed to start within $maxWait seconds." -ForegroundColor Red
    Write-Host "Check container logs:" -ForegroundColor Yellow
    docker logs $containerName
    Read-Host "Press Enter to exit"
}