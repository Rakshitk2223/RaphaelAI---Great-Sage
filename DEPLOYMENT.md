# Deployment Guide for Raphael AI

## Prerequisites

1. **Firebase Project Setup**
   - Create a Firebase project at https://console.firebase.google.com
   - Enable Authentication (Google provider)
   - Enable Firestore Database
   - Enable Cloud Functions

2. **Google Cloud APIs**
   - Enable Google Calendar API
   - Enable Gemini API (AI Studio)
   - Create service account for Calendar API access

3. **API Keys and Credentials**
   - Gemini API key from AI Studio
   - Service account JSON file for Calendar API
   - Firebase project credentials

## Local Development

```bash
# Install dependencies
npm install -g firebase-tools
cd functions && pip install -r requirements.txt
cd ../public && npm install

# Configure environment
cp functions/.env.example functions/.env
# Edit .env with your API keys

# Start development
firebase emulators:start
```

## Production Deployment

### 1. Firebase Setup
```bash
# Login to Firebase
firebase login

# Initialize project (if not done)
firebase init

# Select:
# - Functions (Python)
# - Hosting
# - Firestore
```

### 2. Environment Configuration
```bash
# Set production environment variables
firebase functions:config:set gemini.api_key="your_gemini_key"
firebase functions:config:set google.project_id="your_project_id"

# For calendar integration
firebase functions:config:set google.service_account="base64_encoded_service_account_json"
```

### 3. Build and Deploy
```bash
# Build React app
cd public && npm run build

# Deploy all services
firebase deploy

# Or deploy individually
firebase deploy --only functions
firebase deploy --only hosting
firebase deploy --only firestore
```

### 4. Post-Deployment Setup

1. **Update CORS settings** in Firebase Functions if needed
2. **Configure custom domain** (optional)
3. **Set up monitoring** and alerts
4. **Test all functionality** with production data

## Environment Variables

### Required in functions/.env (local)
```bash
GEMINI_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
FIREBASE_PROJECT_ID=your_project_id
FLASK_ENV=development
```

### Production (Firebase Functions Config)
```bash
firebase functions:config:set gemini.api_key="key"
firebase functions:config:set google.project_id="id"
firebase functions:config:set google.service_account="base64_json"
```

## Security Considerations

1. **Firestore Rules**: Ensure proper user data isolation
2. **API Keys**: Never commit sensitive keys to repository
3. **CORS**: Configure appropriate origins for production
4. **Rate Limiting**: Consider implementing rate limits for API calls
5. **Monitoring**: Set up error tracking and performance monitoring

## Monitoring and Maintenance

- Use Firebase Console for function logs
- Monitor Firestore usage and billing
- Set up alerts for errors or unusual activity
- Regular backup of user data
- Keep dependencies updated

## Troubleshooting

### Common Deployment Issues

1. **Function timeout**: Increase timeout in firebase.json
2. **Memory issues**: Increase memory allocation for functions
3. **Build failures**: Check Python/Node version compatibility
4. **Authentication errors**: Verify service account permissions

### Performance Optimization

1. **Cold starts**: Consider keeping functions warm
2. **Database queries**: Optimize Firestore queries and indexes
3. **Bundle size**: Minimize React bundle size
4. **Caching**: Implement appropriate caching strategies
