# Setup script for Raphael AI development environment
# Run this script to install all necessary dependencies

Write-Host "Setting up Raphael AI development environment..." -ForegroundColor Green

# Check if Firebase CLI is installed
try {
    firebase --version | Out-Null
    Write-Host "✅ Firebase CLI is already installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Firebase CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g firebase-tools
    Write-Host "✅ Firebase CLI installed" -ForegroundColor Green
}

# Check if Python is installed
try {
    python --version | Out-Null
    Write-Host "✅ Python is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11 or higher from https://python.org" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Set-Location "functions"
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}
Set-Location ".."

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install Node.js dependencies" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path "functions\.env")) {
    Write-Host "❌ .env file not found. Copying template..." -ForegroundColor Yellow
    Copy-Item "functions\.env.example" "functions\.env"
    Write-Host "✅ .env template created. Please edit functions\.env with your API keys" -ForegroundColor Green
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit functions\.env with your API keys and credentials" -ForegroundColor White
Write-Host "2. Run 'firebase login' to authenticate with Firebase" -ForegroundColor White
Write-Host "3. Run 'npm start' to start the development server" -ForegroundColor White
Write-Host "4. Run 'npm run deploy' to deploy to production" -ForegroundColor White
