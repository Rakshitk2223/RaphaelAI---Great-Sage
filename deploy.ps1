# PowerShell deployment script for Raphael AI
Write-Host "🚀 Deploying Raphael AI to Firebase..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path "functions\.env")) {
    Write-Host "❌ Error: functions\.env file not found!" -ForegroundColor Red
    Write-Host "Please copy functions\.env.example to functions\.env and fill in your API keys" -ForegroundColor Yellow
    exit 1
}

# Check if Firebase CLI is installed
try {
    firebase --version | Out-Null
} catch {
    Write-Host "❌ Firebase CLI not found. Installing..." -ForegroundColor Red
    npm install -g firebase-tools
}

# Login to Firebase (if not already logged in)
Write-Host "🔐 Checking Firebase authentication..." -ForegroundColor Blue
firebase login

# Deploy Firestore rules and indexes
Write-Host "📄 Deploying Firestore rules and indexes..." -ForegroundColor Blue
firebase deploy --only firestore

# Deploy Cloud Functions
Write-Host "⚡ Deploying Cloud Functions..." -ForegroundColor Blue
firebase deploy --only functions

# Deploy Frontend
Write-Host "🌐 Deploying Frontend..." -ForegroundColor Blue
firebase deploy --only hosting

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🔗 Your app is available at: https://raphael-great-sage.web.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the authentication by signing in with Google"
Write-Host "2. Try these example commands:"
Write-Host "   - 'Remember my cat's name is Whiskers'"
Write-Host "   - 'What's my cat's name?'"
Write-Host "   - 'Add meeting tomorrow at 3 PM'"
Write-Host "   - 'Calculate 25 * 4'"
Write-Host "   - 'I have 2000rs this month, 40rs/day for college'"
