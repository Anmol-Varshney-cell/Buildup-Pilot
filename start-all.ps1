# One-command starter for BUILD UP + SKILL UP
# Run: .\start-all.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUILD UP + SKILL UP Auto Starter" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Check / Install PM2
Write-Host "`n[1/3] Checking PM2..." -ForegroundColor Yellow
$pm2Check = npm list -g pm2 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "PM2 not found. Installing..." -ForegroundColor Red
    npm install -g pm2
} else {
    Write-Host "PM2 is already installed." -ForegroundColor Green
}

# 2. Create logs directory
Write-Host "`n[2/3] Creating logs directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
Write-Host "Logs directory ready." -ForegroundColor Green

# 3. Start all services with PM2
Write-Host "`n[3/3] Starting all services..." -ForegroundColor Yellow
pm2 start ecosystem.config.cjs

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nBUILD UP:     http://localhost:5000" -ForegroundColor Cyan
Write-Host "BACKEND:      http://localhost:4000" -ForegroundColor Cyan
Write-Host "JUDGE:        http://localhost:5001" -ForegroundColor Cyan
Write-Host "SKILL UP:     http://localhost:5173" -ForegroundColor Cyan
Write-Host "`nCommands:" -ForegroundColor Gray
Write-Host "  pm2 status       - View running services" -ForegroundColor Gray
Write-Host "  pm2 logs         - View all logs" -ForegroundColor Gray
Write-Host "  pm2 monit        - Real-time monitor" -ForegroundColor Gray
Write-Host "  pm2 stop all     - Stop all services" -ForegroundColor Gray

