# Gemini AI service - handles all interactions with Google Gemini API
import os
import json
import re
from datetime import datetime
import google.generativeai as genai

# Initialize Gemini model
try:
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        print("Gemini AI model initialized")
    else:
        print("GEMINI_API_KEY not found - Gemini features will be disabled")
        model = None
except Exception as e:
    print(f"Error initializing Gemini AI: {e}")
    model = None


def get_gemini_response(user_message, conversation_history=None, user_personal_context=None):
    """
    Get a response from Gemini AI with context.
    
    Args:
        user_message (str): The current user message
        conversation_history (list, optional): List of previous chat messages
        user_personal_context (dict, optional): User-specific facts and data
        
    Returns:
        str: Gemini's text response
    """
    try:
        if model is None:
            return "I'm sorry, but my AI services are currently unavailable. Please try again later."
        
        # Build context prompt
        context_parts = []
        
        # Add personal context
        if user_personal_context:
            context_parts.append("Here's what I know about you:")
            if 'memories' in user_personal_context and user_personal_context['memories']:
                context_parts.append(f"Recent memories: {'; '.join(user_personal_context['memories'][:5])}")
            if 'budget' in user_personal_context and user_personal_context['budget']:
                context_parts.append(f"Budget info: {user_personal_context['budget']}")
            if 'homework' in user_personal_context and user_personal_context['homework']:
                context_parts.append(f"Pending homework: {'; '.join(user_personal_context['homework'][:3])}")
            if 'timetable' in user_personal_context and user_personal_context['timetable']:
                context_parts.append(f"Today's classes: {'; '.join(user_personal_context['timetable'])}")
        
        # Add conversation history
        if conversation_history:
            context_parts.append("\nRecent conversation:")
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                context_parts.append(f"{msg.get('sender', 'Unknown')}: {msg.get('text', '')}")
        
        # Build the full prompt
        full_prompt = f"""
You are Raphael, a helpful personal AI assistant. You have access to the user's personal data and can help them with various tasks.

{chr(10).join(context_parts) if context_parts else "No additional context available."}

Current user message: "{user_message}"

Based on this message and context, respond naturally and helpfully as Raphael. If the user is asking you to:

1. **Remember something** (e.g., "remember", "my name is", "I like") - Acknowledge that you'll remember it
2. **Recall information** (e.g., "what do you know about", "tell me about") - Use the memories from context
3. **Schedule events** (e.g., "add meeting", "schedule", "appointment") - Help them plan the event
4. **Get calendar info** (e.g., "what's my schedule", "events today") - Refer to their calendar
5. **Calculate something** (e.g., math expressions, "what is 5+3") - Provide the calculation
6. **Manage homework** (e.g., "homework", "assignments", "due") - Help with homework tracking
7. **Handle budget** (e.g., "expense", "budget", "spent money") - Assist with budget management
8. **Get timetable** (e.g., "classes today", "my schedule") - Show their class schedule

Respond conversationally and include specific actions if needed. Keep responses concise but helpful.
"""
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return "I'm having trouble processing your request right now. Please try again."


def parse_gemini_intent(user_message, gemini_response_text):
    """
    Parse Gemini's response to identify specific intents and extract structured data.
    
    Args:
        user_message (str): Original user message
        gemini_response_text (str): Gemini's response
        
    Returns:
        dict: Parsed intent information with action type and extracted data
    """
    try:
        # Convert to lowercase for matching
        message_lower = user_message.lower()
        response_lower = gemini_response_text.lower()
        
        intent_data = {
            'action': 'general',
            'confidence': 0.5,
            'entities': {},
            'response': gemini_response_text
        }
        
        # Memory storage detection
        if any(keyword in message_lower for keyword in ['remember', 'my', 'i am', 'i have', 'i like', 'my name is']):
            intent_data['action'] = 'store_memory'
            intent_data['confidence'] = 0.9
            intent_data['entities'] = {'memory_text': user_message}
        
        # Memory retrieval detection
        elif any(keyword in message_lower for keyword in ['what did i tell you', 'do you remember', 'what do you know about', 'tell me about']):
            intent_data['action'] = 'retrieve_memory'
            intent_data['confidence'] = 0.8
            # Extract query term
            query_patterns = [r'about (.+)', r'remember (.+)', r'know about (.+)']
            for pattern in query_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    intent_data['entities']['query'] = match.group(1)
                    break
        
        # Calendar event detection
        elif any(keyword in message_lower for keyword in ['add meeting', 'schedule', 'appointment', 'calendar', 'add event', 'meeting']):
            intent_data['action'] = 'add_calendar_event'
            intent_data['confidence'] = 0.8
            intent_data['entities'] = extract_event_details(user_message)
        
        # Calendar query detection
        elif any(keyword in message_lower for keyword in ['today', 'schedule today', 'events today', 'what\'s my schedule']):
            intent_data['action'] = 'get_calendar_events'
            intent_data['confidence'] = 0.9
        
        # Calculation detection
        elif any(keyword in message_lower for keyword in ['calculate', 'what is', 'math']) or re.search(r'[\+\-\*\/\=]', user_message):
            intent_data['action'] = 'calculate'
            intent_data['confidence'] = 0.9
            intent_data['entities'] = {'expression': user_message}
        
        # Homework detection
        elif any(keyword in message_lower for keyword in ['homework', 'assignment', 'due']):
            if any(add_keyword in message_lower for add_keyword in ['add', 'new', 'have']):
                intent_data['action'] = 'add_homework'
                intent_data['entities'] = extract_homework_details(user_message)
            else:
                intent_data['action'] = 'get_homework'
            intent_data['confidence'] = 0.8
        
        # Budget detection
        elif any(keyword in message_lower for keyword in ['budget', 'expense', 'spent', 'money', 'cost', 'paid']):
            if any(add_keyword in message_lower for add_keyword in ['spent', 'paid', 'bought', 'cost']):
                intent_data['action'] = 'add_expense'
                intent_data['entities'] = extract_expense_details(user_message)
            elif any(set_keyword in message_lower for set_keyword in ['set budget', 'monthly budget']):
                intent_data['action'] = 'set_budget'
                intent_data['entities'] = extract_budget_amount(user_message)
            else:
                intent_data['action'] = 'get_budget'
            intent_data['confidence'] = 0.8
        
        # Timetable detection
        elif any(keyword in message_lower for keyword in ['classes', 'timetable', 'class schedule']):
            intent_data['action'] = 'get_timetable'
            intent_data['confidence'] = 0.8
        
        return intent_data
        
    except Exception as e:
        print(f"Error parsing intent: {e}")
        return {
            'action': 'general',
            'confidence': 0.5,
            'entities': {},
            'response': gemini_response_text
        }


def extract_event_details(message):
    """Extract event details from user message."""
    entities = {}
    
    # Extract time patterns
    time_patterns = [
        r'at (\d{1,2}:\d{2})',
        r'at (\d{1,2})\s*(am|pm)',
        r'(\d{1,2}:\d{2})\s*(am|pm)?'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, message.lower())
        if match:
            entities['time'] = match.group(1)
            if len(match.groups()) > 1 and match.group(2):
                entities['time'] += match.group(2)
            break
    
    # Extract date patterns
    if 'tomorrow' in message.lower():
        entities['date'] = 'tomorrow'
    elif 'today' in message.lower():
        entities['date'] = 'today'
    elif 'next week' in message.lower():
        entities['date'] = 'next_week'
    
    # Extract event title (simple heuristic)
    if 'meeting' in message.lower():
        entities['title'] = 'Meeting'
    elif 'appointment' in message.lower():
        entities['title'] = 'Appointment'
    else:
        # Try to extract from context
        words = message.split()
        if len(words) > 2:
            entities['title'] = ' '.join(words[1:4])  # Take a few words as title
    
    return entities


def extract_homework_details(message):
    """Extract homework details from user message."""
    entities = {}
    
    # Look for subject patterns
    subjects = ['math', 'science', 'english', 'history', 'physics', 'chemistry', 'biology']
    for subject in subjects:
        if subject in message.lower():
            entities['subject'] = subject.title()
            break
    
    # Look for due date patterns
    if 'tomorrow' in message.lower():
        entities['due_date'] = 'tomorrow'
    elif 'next week' in message.lower():
        entities['due_date'] = 'next_week'
    elif 'friday' in message.lower():
        entities['due_date'] = 'friday'
    
    # Extract description (everything after common homework keywords)
    hw_keywords = ['homework', 'assignment', 'due']
    for keyword in hw_keywords:
        if keyword in message.lower():
            parts = message.lower().split(keyword, 1)
            if len(parts) > 1:
                entities['description'] = parts[1].strip()
                break
    
    return entities


def extract_expense_details(message):
    """Extract expense details from user message."""
    entities = {}
    
    # Extract amount patterns
    amount_patterns = [
        r'\$(\d+(?:\.\d{2})?)',
        r'(\d+(?:\.\d{2})?)\s*dollars?',
        r'(\d+(?:\.\d{2})?)\s*bucks?',
        r'(\d+(?:\.\d{2})?)'
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, message)
        if match:
            entities['amount'] = float(match.group(1))
            break
    
    # Extract category patterns
    categories = ['food', 'transportation', 'entertainment', 'shopping', 'groceries', 'gas', 'coffee']
    for category in categories:
        if category in message.lower():
            entities['category'] = category
            break
    
    # Default category if none found
    if 'category' not in entities:
        entities['category'] = 'general'
    
    return entities


def extract_budget_amount(message):
    """Extract budget amount from user message."""
    entities = {}
    
    # Extract amount patterns
    amount_patterns = [
        r'\$(\d+(?:\.\d{2})?)',
        r'(\d+(?:\.\d{2})?)\s*dollars?'
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, message)
        if match:
            entities['budget_amount'] = float(match.group(1))
            break
    
    return entities


def generate_structured_prompt(intent, user_data, specific_request):
    """
    Generate a structured prompt for specific intents.
    
    Args:
        intent (str): The identified intent
        user_data (dict): User's personal data
        specific_request (str): The specific request details
        
    Returns:
        str: Formatted prompt for Gemini
    """
    prompts = {
        'calendar_event': f"""
        Help the user create a calendar event. 
        Request: {specific_request}
        User context: {user_data.get('recent_events', 'No recent events')}
        
        Extract and format:
        - Event title
        - Date and time
        - Duration
        - Any additional details
        
        Respond naturally while providing the structured information.
        """,
        
        'budget_analysis': f"""
        Help the user with budget analysis.
        Request: {specific_request}
        Current budget: {user_data.get('budget', 'No budget set')}
        Recent expenses: {user_data.get('recent_expenses', 'No recent expenses')}
        
        Provide insights and recommendations based on their spending patterns.
        """,
        
        'homework_reminder': f"""
        Help the user manage their homework.
        Request: {specific_request}
        Pending assignments: {user_data.get('homework', 'No pending homework')}
        Class schedule: {user_data.get('timetable', 'No schedule available')}
        
        Provide helpful reminders and study suggestions.
        """
    }
    
    return prompts.get(intent, f"Help the user with: {specific_request}")


# Helper function for conversation history management
def format_conversation_history(messages, max_length=5):
    """
    Format conversation history for Gemini context.
    
    Args:
        messages (list): List of message dicts with 'sender' and 'text' keys
        max_length (int): Maximum number of messages to include
        
    Returns:
        list: Formatted conversation history
    """
    if not messages:
        return []
    
    # Take the most recent messages
    recent_messages = messages[-max_length:] if len(messages) > max_length else messages
    
    formatted = []
    for msg in recent_messages:
        sender = msg.get('sender', 'unknown')
        text = msg.get('text', '')
        if sender == 'user':
            formatted.append(f"User: {text}")
        elif sender == 'raphael':
            formatted.append(f"Raphael: {text}")
    
    return formatted
