import os
import json
import re
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import firestore
from google.cloud import speech
from google.cloud import texttospeech
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Google Cloud clients
db = firestore.Client()
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

# Configure Gemini AI
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service(user_id):
    """Get Google Calendar service for a user."""
    try:
        # In production, you'd retrieve user's OAuth credentials from Firestore
        # For now, using service account credentials as placeholder
        credentials = service_account.Credentials.from_service_account_file(
            os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'), scopes=SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error setting up calendar service: {e}")
        return None

def authenticate_user(user_id):
    """Placeholder authentication function."""
    # In production, verify Firebase ID token
    if user_id and len(user_id) > 0:
        return True
    return False

def store_memory(user_id, memory_text, category="general"):
    """Store a memory/fact in Firestore."""
    try:
        doc_ref = db.collection('users').document(user_id).collection('memories').document()
        doc_ref.set({
            'text': memory_text,
            'category': category,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'created_at': datetime.now().isoformat()
        })
        return True
    except Exception as e:
        print(f"Error storing memory: {e}")
        return False

def retrieve_memories(user_id, query=None):
    """Retrieve memories from Firestore."""
    try:
        memories_ref = db.collection('users').document(user_id).collection('memories')
        
        if query:
            # Simple text search in memories
            docs = memories_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(20).stream()
            relevant_memories = []
            for doc in docs:
                memory_data = doc.to_dict()
                if query.lower() in memory_data['text'].lower():
                    relevant_memories.append(memory_data['text'])
            return relevant_memories
        else:
            # Return recent memories
            docs = memories_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()
            return [doc.to_dict()['text'] for doc in docs]
    except Exception as e:
        print(f"Error retrieving memories: {e}")
        return []

def add_calendar_event(user_id, summary, start_time, end_time=None, description=""):
    """Add an event to user's Google Calendar."""
    try:
        service = get_calendar_service(user_id)
        if not service:
            return False, "Calendar service unavailable"
        
        if not end_time:
            end_time = start_time + timedelta(hours=1)
        
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        return True, f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        print(f"Error adding calendar event: {e}")
        return False, str(e)

def get_todays_events(user_id):
    """Get today's calendar events."""
    try:
        service = get_calendar_service(user_id)
        if not service:
            return []
        
        today = datetime.now().date()
        start_time = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
        end_time = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        return [{'summary': event['summary'], 'start': event['start'].get('dateTime', event['start'].get('date'))} for event in events]
    except Exception as e:
        print(f"Error getting today's events: {e}")
        return []

def perform_calculation(expression):
    """Safely perform basic calculations."""
    try:
        # Remove any non-mathematical characters for safety
        clean_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        result = eval(clean_expr)
        return f"The result is: {result}"
    except Exception as e:
        return "I couldn't perform that calculation. Please check your expression."

def get_timetable(user_id, day=None):
    """Get timetable/classes for a specific day."""
    try:
        if not day:
            day = datetime.now().strftime('%A').lower()
        
        timetable_ref = db.collection('users').document(user_id).collection('timetable').document(day)
        doc = timetable_ref.get()
        
        if doc.exists:
            classes = doc.to_dict().get('classes', [])
            return classes
        return []
    except Exception as e:
        print(f"Error getting timetable: {e}")
        return []

def get_homework_reminders(user_id):
    """Get homework reminders."""
    try:
        homework_ref = db.collection('users').document(user_id).collection('homework')
        docs = homework_ref.where('completed', '==', False).order_by('due_date').stream()
        
        homework_list = []
        for doc in docs:
            hw_data = doc.to_dict()
            homework_list.append(f"{hw_data['subject']}: {hw_data['description']} (Due: {hw_data['due_date']})")
        
        return homework_list
    except Exception as e:
        print(f"Error getting homework: {e}")
        return []

def process_with_gemini(user_id, message, context=None):
    """Process message with Gemini AI and determine intent."""
    try:
        # Build context with user memories and current info
        memories = retrieve_memories(user_id)
        context_text = f"""
        You are Raphael, a personal AI assistant. Here's what you know about the user:
        Recent memories: {'; '.join(memories) if memories else 'None'}
        
        The user said: "{message}"
        
        Analyze this message and determine if it's:
        1. A memory to store (starts with "remember", "my", contains personal info)
        2. A memory retrieval (asking about something previously told)
        3. A calendar event request (mentions scheduling, meetings, appointments)
        4. A calculation (contains math expressions)
        5. A timetable query (asking about classes, schedule)
        6. A homework query (asking about assignments, homework)
        7. A general conversation
        
        Respond naturally as Raphael, and if it's a specific request type, format your response to include the action needed.
        """
        
        response = model.generate_content(context_text)
        return response.text
    except Exception as e:
        print(f"Error with Gemini: {e}")
        return "I'm having trouble processing your request right now. Please try again."

def speech_to_text(audio_content):
    """Convert speech to text using Google Cloud Speech-to-Text."""
    try:
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
        )
        
        response = speech_client.recognize(config=config, audio=audio)
        
        if response.results:
            return response.results[0].alternatives[0].transcript
        return ""
    except Exception as e:
        print(f"Error in speech to text: {e}")
        return ""

def text_to_speech(text):
    """Convert text to speech using Google Cloud Text-to-Speech."""
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        return response.audio_content
    except Exception as e:
        print(f"Error in text to speech: {e}")
        return None

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', '')
        
        # Authenticate user
        if not authenticate_user(user_id):
            return jsonify({'error': 'Authentication failed'}), 401
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process message with Gemini to understand intent
        response_text = process_with_gemini(user_id, message)
        
        # Check for specific intents and perform actions
        message_lower = message.lower()
        
        # Memory storage
        if any(keyword in message_lower for keyword in ['remember', 'my', 'i am', 'i have', 'i like']):
            if store_memory(user_id, message):
                response_text += "\n\nI'll remember that for you!"
        
        # Memory retrieval
        elif any(keyword in message_lower for keyword in ['what did i tell you', 'do you remember', 'what do you know about']):
            memories = retrieve_memories(user_id, message)
            if memories:
                response_text += f"\n\nHere's what I remember: {'; '.join(memories)}"
        
        # Calendar events
        elif any(keyword in message_lower for keyword in ['add meeting', 'schedule', 'appointment', 'calendar']):
            # Simple parsing for demo - in production use more sophisticated NLP
            if 'tomorrow' in message_lower and 'pm' in message_lower:
                tomorrow = datetime.now() + timedelta(days=1)
                start_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)  # Default 3 PM
                success, result = add_calendar_event(user_id, "Meeting", start_time)
                if success:
                    response_text += f"\n\nEvent added successfully!"
        
        # Today's events
        elif any(keyword in message_lower for keyword in ['today', 'schedule today', 'events today']):
            events = get_todays_events(user_id)
            if events:
                event_list = "\n".join([f"- {event['summary']} at {event['start']}" for event in events])
                response_text += f"\n\nHere are your events today:\n{event_list}"
            else:
                response_text += "\n\nYou have no events scheduled for today."
        
        # Calculations
        elif any(keyword in message_lower for keyword in ['calculate', 'what is', '+', '-', '*', '/']):
            calc_result = perform_calculation(message)
            response_text += f"\n\n{calc_result}"
        
        # Timetable queries
        elif any(keyword in message_lower for keyword in ['classes today', 'timetable', 'schedule', 'class']):
            classes = get_timetable(user_id)
            if classes:
                class_list = "\n".join([f"- {cls}" for cls in classes])
                response_text += f"\n\nHere are your classes:\n{class_list}"
            else:
                response_text += "\n\nNo classes found for today."
        
        # Homework reminders
        elif any(keyword in message_lower for keyword in ['homework', 'assignments', 'due']):
            homework = get_homework_reminders(user_id)
            if homework:
                hw_list = "\n".join([f"- {hw}" for hw in homework])
                response_text += f"\n\nHere's your pending homework:\n{hw_list}"
            else:
                response_text += "\n\nYou have no pending homework!"
        
        # Generate audio response (optional)
        audio_content = None
        if data.get('generate_audio', False):
            audio_content = text_to_speech(response_text)
        
        return jsonify({
            'response': response_text,
            'user_id': user_id,
            'audio': audio_content.hex() if audio_content else None
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_endpoint():
    """Endpoint for speech-to-text conversion."""
    try:
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({'error': 'Audio file is required'}), 400
        
        audio_content = audio_file.read()
        transcript = speech_to_text(audio_content)
        
        return jsonify({'transcript': transcript})
        
    except Exception as e:
        print(f"Error in speech-to-text endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
