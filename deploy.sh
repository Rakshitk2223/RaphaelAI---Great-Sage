#!/bin/bash
# Deployment script for Raphael AI

echo "🚀 Deploying Raphael AI to Firebase..."

# Check if .env file exists
if [ ! -f "functions/.env" ]; then
    echo "❌ Error: functions/.env file not found!"
    echo "Please copy functions/.env.example to functions/.env and fill in your API keys"
    exit 1
fi

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Login to Firebase (if not already logged in)
echo "🔐 Checking Firebase authentication..."
firebase login --no-localhost

# Deploy Firestore rules and indexes
echo "📄 Deploying Firestore rules and indexes..."
firebase deploy --only firestore

# Deploy Cloud Functions
echo "⚡ Deploying Cloud Functions..."
firebase deploy --only functions

# Deploy Frontend
echo "🌐 Deploying Frontend..."
firebase deploy --only hosting

echo "✅ Deployment complete!"
echo "🔗 Your app is available at: https://raphael-great-sage.web.app"
echo ""
echo "📝 Next steps:"
echo "1. Test the authentication by signing in with Google"
echo "2. Try these example commands:"
echo "   - 'Remember my cat's name is Whiskers'"
echo "   - 'What's my cat's name?'"
echo "   - 'Add meeting tomorrow at 3 PM'"
echo "   - 'Calculate 25 * 4'"
echo "   - 'I have 2000rs this month, 40rs/day for college'"
