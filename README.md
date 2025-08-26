# Raphael AI - Great Sage Assistant

A voice-driven personal AI assistant inspired by "Great Sage" from anime. Raphael AI helps you manage your daily life with memory, calendar integration, budget tracking, and homework assistance.

## 🌟 Features

- **🎤 Voice Interaction**: Full voice input/output using Web Speech API (no additional costs)
- **🧠 Personal Memory**: Stores and recalls your personal information and preferences
- **📅 Calendar Integration**: Manages your schedule and events through Google Calendar
- **💰 Budget Tracking**: Tracks income, expenses, and provides financial insights
- **📚 Homework Assistant**: Helps manage tasks and assignments
- **🔐 Secure Authentication**: Firebase Authentication with Google Sign-in
- **☁️ Cloud Storage**: All data securely stored in Firestore with user-scoped access

## 🏗️ Architecture

### Backend (Firebase Cloud Functions - Python)
- **Flask Application**: Main API server with RESTful endpoints
- **Firebase Admin SDK**: Authentication and Firestore integration
- **Google Gemini AI**: Natural language processing and intent parsing
- **Google Calendar API**: Event management and scheduling
- **Modular Services**: Clean separation of concerns with service pattern

### Frontend (React)
- **Modern React**: Functional components with hooks
- **Component-based**: Modular UI components (AuthUI, ChatWindow, MessageInput)
- **Speech Integration**: Custom hooks for speech recognition and synthesis
- **Firebase SDK**: Client-side authentication and real-time updates
- **Responsive Design**: Clean, modern interface that works on all devices

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Firebase CLI
- Google Cloud Project with required APIs enabled

### Environment Setup

1. **Clone and install dependencies:**
```bash
cd RaphaelAI
npm install -g firebase-tools
cd functions && pip install -r requirements.txt
cd ../public && npm install
```

2. **Configure environment variables:**
```bash
cd functions
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `GOOGLE_APPLICATION_CREDENTIALS`: Service account JSON file path
- `FIREBASE_PROJECT_ID`: Your Firebase project ID

3. **Start development environment:**
```bash
# From project root
firebase emulators:start
```

This starts:
- Functions emulator: http://localhost:5001
- Firestore emulator: http://localhost:8080  
- Hosting: http://localhost:5000
- Firebase UI: http://localhost:4000

## 📁 Project Structure

```
RaphaelAI/
├── functions/                 # Backend Cloud Functions
│   ├── main.py               # Main Flask application
│   ├── requirements.txt      # Python dependencies
│   ├── services/            # Business logic services
│   │   ├── firestore_service.py    # Database operations
│   │   ├── gemini_service.py       # AI integration
│   │   └── calendar_service.py     # Calendar management
│   └── utils/               # Utility functions
│       ├── auth_middleware.py      # Authentication
│       └── calculations.py         # Math operations
├── public/                   # Frontend React app
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── components/      # UI components
│   │   ├── hooks/          # Custom React hooks
│   │   └── services/       # API communication
│   ├── package.json        # Frontend dependencies
│   └── index.html          # Entry point
├── firebase.json           # Firebase configuration
├── firestore.rules        # Database security rules
└── package.json           # Project metadata
```

## 🔧 Development

### Backend Development
```bash
cd functions
python main.py  # Local development server
```

### Frontend Development
```bash
cd public
npm start  # React development server
```

### Testing
```bash
# Backend
cd functions && python -m pytest tests/

# Linting
cd functions && flake8 .
cd functions && black .  # Code formatting
```

## 📋 API Endpoints

### POST /chat
Main conversation endpoint with authentication required.

**Request:**
```json
{
  "message": "Remember that I love chocolate ice cream",
  "idToken": "firebase_id_token"
}
```

**Response:**
```json
{
  "message": "I'll remember that you love chocolate ice cream! 🍦",
  "intent": "store_memory",
  "user_id": "user123"
}
```

### GET /user-data
Get user's personal data summary (authenticated).

### GET /health
Health check endpoint.

## 🎯 Supported Intents

- **Memory Management**: "Remember that...", "What do you know about..."
- **Calendar Events**: "Schedule a meeting...", "What's on my calendar?"
- **Budget Tracking**: "I spent $20 on lunch", "What's my budget?"
- **Task Management**: "Add homework: Math assignment", "What are my tasks?"
- **Calculations**: "What's 15% of 200?", "Calculate compound interest"
- **General Chat**: Conversations and Q&A

## 🔐 Security

- Firebase Authentication with Google Sign-in
- User-scoped data isolation in Firestore
- Server-side ID token verification
- Secure API endpoints with authentication middleware
- Environment variables for sensitive data

## 🚀 Deployment

### Production Deployment
```bash
# Deploy all services
firebase deploy

# Deploy specific services
firebase deploy --only functions
firebase deploy --only hosting
firebase deploy --only firestore
```

### Environment Configuration
Set production environment variables in Firebase Functions:
```bash
firebase functions:config:set gemini.api_key="your_key_here"
firebase functions:config:set google.project_id="your_project_id"
```

## 🎨 Customization

### Adding New Intents
1. Update `gemini_service.py` intent parsing
2. Add action handling in `main.py` `execute_action()` function
3. Create corresponding service functions if needed

### UI Customization
- Modify `App.css` for styling
- Update components in `public/src/components/`
- Customize voice settings in speech hooks

## 🐛 Troubleshooting

### Common Issues

**"GEMINI_API_KEY not found"**
- Ensure `.env` file exists in `functions/` directory
- Verify API key is correctly set

**Authentication errors**
- Check Firebase project configuration
- Verify service account permissions
- Ensure Firestore security rules are properly configured

**Voice features not working**
- Ensure HTTPS connection (required for Web Speech API)
- Check browser compatibility
- Verify microphone permissions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📞 Support

- Create an issue for bug reports or feature requests
- Check existing issues before creating new ones
- Provide detailed information for faster resolution

---

**Raphael AI** - Your personal Great Sage assistant 🧙‍♂️✨
