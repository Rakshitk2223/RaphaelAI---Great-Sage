# Raphael AI - Personal AI Assistant

A sophisticated personal AI assistant built with Flask (Python) backend and React frontend, deployed on Google Cloud Platform with Firebase integration.

## Features

### Core Capabilities
- **Natural Language Processing**: Powered by Google's Gemini AI for understanding and generating human-like responses
- **Voice Interaction**: Browser-based speech-to-text and text-to-speech using Web Speech APIs
- **Personal Memory**: Store and retrieve personal information using Google Cloud Firestore
- **Calendar Integration**: Add events and query your Google Calendar
- **Educational Assistant**: Manage timetables and homework reminders
- **Budget Management**: Track monthly budgets and daily expenses
- **Calculator**: Perform basic mathematical calculations
- **User Authentication**: Secure login with Google Firebase Authentication

### Technical Features
- **Real-time Chat Interface**: Modern, responsive React frontend with Tailwind CSS
- **Cloud-Native**: Designed for Google Cloud Platform deployment
- **Secure**: Proper Firebase authentication with ID token verification
- **Scalable**: Serverless architecture using Cloud Functions
- **Browser-Based Voice**: No server-side STT/TTS dependencies

## Project Structure

```
RaphaelAI/
├── functions/             # Python Flask backend (Cloud Function)
│   ├── main.py           # Main Flask application with all AI capabilities
│   ├── requirements.txt  # Python dependencies
│   └── .env.example     # Environment variables template
├── public/               # React frontend web app
│   ├── src/
│   │   ├── App.js       # Main React component with chat interface
│   │   └── index.js     # React app entry point
│   └── index.html       # HTML template with Tailwind CSS
├── firebase.json         # Firebase project configuration
├── .firebaserc          # Firebase project settings
├── firestore.rules      # Firestore security rules
├── firestore.indexes.json # Firestore database indexes
└── .gitignore           # Git ignore file
```

## Setup Instructions

### Prerequisites
- Google Cloud Platform account
- Firebase project
- Node.js and npm (for frontend development)
- Python 3.11+ (for backend development)
- Firebase CLI tools

### 1. Firebase Project Setup

1. Create a new Firebase project at [https://console.firebase.google.com](https://console.firebase.google.com)
2. Enable the following services:
   - Authentication (Google provider)
   - Firestore Database
   - Cloud Functions
   - Hosting

### 2. Google Cloud Platform Setup

1. Enable the following APIs in Google Cloud Console:
   - Google Calendar API
   - Firestore API
   - Cloud Functions API

2. Create a service account and download the JSON key file for:
   - Google Cloud services (for Calendar API)
   - Firebase Admin SDK (for user authentication)
3. Get a Gemini AI API key from [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

### 3. Environment Configuration

1. Copy `functions/.env.example` to `functions/.env`
2. Fill in your actual API keys and configuration:

```bash
# functions/.env
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
FIREBASE_SERVICE_ACCOUNT_KEY=path/to/your/firebase-admin-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
GEMINI_API_KEY=your-gemini-api-key
FLASK_ENV=production
PORT=8080
```

3. Update Firebase configuration in `public/src/App.js`:

```javascript
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "your-sender-id",
  appId: "your-app-id"
};
```

4. Update `.firebaserc` with your project ID:

```json
{
  "projects": {
    "default": "your-project-id"
  }
}
```

### 4. Local Development

1. Install Firebase CLI:
```bash
npm install -g firebase-tools
```

2. Login to Firebase:
```bash
firebase login
```

3. Install Python dependencies:
```bash
cd functions
pip install -r requirements.txt
```

4. Start the local development server:
```bash
firebase emulators:start
```

### 5. Deployment

1. Deploy to Firebase:
```bash
firebase deploy
```

This will deploy:
- Cloud Functions (Python Flask backend)
- Firebase Hosting (React frontend)
- Firestore rules and indexes

### 6. Testing the Application

1. Open your deployed app URL (provided after deployment)
2. Sign in with your Google account
3. Try these example interactions:
   - "Remember my favorite color is blue"
   - "What's my favorite color?"
   - "Add a meeting tomorrow at 3 PM"
   - "What are my events today?"
   - "What's 25 * 4?"
   - "What classes do I have today?" (after setting up timetable)

## API Endpoints

### POST /chat
Main chat endpoint for interacting with Raphael AI.

**Request:**
```json
{
  "message": "Remember my car is red",
  "idToken": "firebase-id-token"
}
```

**Response:**
```json
{
  "message": "I'll remember that your car is red! ✅ I've stored this information in my memory.",
  "user_id": "firebase-user-id", 
  "intent": "MEMORY_STORE"
}
```

### POST /speech-to-text
**DEPRECATED** - Speech-to-text is now handled in the browser using Web Speech API.

### GET /user-data
Get user's personal data summary (requires authentication).

### GET /health
Health check endpoint.

## Data Structure

### Firestore Collections

#### /users/{userId}/memories
```json
{
  "text": "My car is red",
  "category": "general",
  "timestamp": "2024-01-01T12:00:00Z",
  "created_at": "2024-01-01T12:00:00.000Z"
}
```

#### /users/{userId}/timetable/{day}
```json
{
  "classes": [
    "Math 101 - 9:00 AM",
    "Physics 201 - 11:00 AM",
    "Chemistry Lab - 2:00 PM"
  ]
}
```

#### /users/{userId}/homework
```json
{
  "subject": "Mathematics",
  "description": "Complete Chapter 5 exercises",
  "due_date": "2024-01-15",
  "completed": false,
  "created_at": "2024-01-01T12:00:00.000Z"
}
```

## Security

- **Authentication**: All requests require valid Firebase user authentication
- **Data Isolation**: Users can only access their own data through Firestore security rules
- **API Keys**: All sensitive credentials are stored as environment variables
- **CORS**: Properly configured for secure cross-origin requests

## Customization

### Adding New Capabilities

1. **Backend**: Add new functions in `functions/main.py`
2. **Intent Recognition**: Update the Gemini prompt in `process_with_gemini()`
3. **Data Storage**: Add new Firestore collections as needed
4. **Frontend**: Update the UI in `public/src/App.js`

### Styling

The frontend uses Tailwind CSS for styling. Customize the design by:
- Modifying classes in `App.js`
- Adding custom CSS in `index.html`
- Updating the Tailwind configuration

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify Firebase configuration and API keys
2. **CORS Issues**: Ensure Flask-CORS is properly configured
3. **Speech Recognition**: Check browser compatibility and microphone permissions
4. **Firestore Permissions**: Verify security rules and user authentication

### Logs

- **Backend Logs**: View in Google Cloud Console > Cloud Functions
- **Frontend Errors**: Check browser developer console
- **Firestore**: Monitor in Firebase Console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review Google Cloud and Firebase documentation
- Open an issue in the repository
