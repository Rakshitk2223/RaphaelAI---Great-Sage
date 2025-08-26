"""
Gemini AI service for Raphael AI
Handles all interactions with Google's Gemini AI model
"""

import os
import json
import re
from datetime import datetime
import google.generativeai as genai

# Initialize Gemini AI
gemini_api_key = os.environ.get('GEMINI_API_KEY')
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
    print("✅ Gemini AI initialized successfully")
else:
    model = None
    print("❌ GEMINI_API_KEY not found")


def get_gemini_response(message, conversation_history=None, user_context=None):
    """
    Get response from Gemini AI with full context
    
    Args:
        message (str): User's current message
        conversation_history (list): Recent conversation history
        user_context (dict): User's personal context (memories, tasks, etc.)
    
    Returns:
        str: AI response
    """
    if not model:
        return "Sorry, AI services are currently unavailable. Please check your API configuration."
    
    try:
        # Build comprehensive context for Gemini
        system_prompt = build_system_prompt(user_context)
        full_prompt = build_full_prompt(system_prompt, conversation_history, message)
        
        # Get response from Gemini
        response = model.generate_content(full_prompt)
        ai_response = response.text if response.text else "I'm sorry, I couldn't generate a response."
        
        return ai_response
        
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return "I encountered an error while processing your request. Please try again."


def build_system_prompt(user_context=None):
    """Build the system prompt with user context"""
    base_prompt = """You are Raphael, an intelligent personal AI assistant inspired by Great Sage. 
You are helpful, friendly, and knowledgeable. You can:

- Remember personal information and preferences
- Help with calendar management and scheduling
- Assist with budget tracking and calculations
- Manage tasks and homework
- Have natural conversations
- Provide helpful advice and information

Be conversational, empathetic, and proactive in helping the user."""
    
    if user_context:
        context_sections = []
        
        # Add memories
        if user_context.get('memories'):
            memories_text = '; '.join(user_context['memories'][:5])
            context_sections.append(f"Personal memories: {memories_text}")
        
        # Add budget info
        if user_context.get('budget'):
            context_sections.append(f"Budget status: {user_context['budget']}")
        
        # Add tasks
        if user_context.get('tasks'):
            tasks_text = '; '.join(user_context['tasks'][:3])
            context_sections.append(f"Current tasks: {tasks_text}")
        
        if context_sections:
            context_prompt = "\n\nCurrent user context:\n" + '\n'.join(context_sections)
            base_prompt += context_prompt
    
    return base_prompt


def build_full_prompt(system_prompt, conversation_history, current_message):
    """Build the complete prompt for Gemini"""
    prompt_parts = [system_prompt]
    
    # Add conversation history
    if conversation_history:
        prompt_parts.append("\nRecent conversation:")
        for msg in conversation_history[-6:]:  # Last 6 messages
            role = "User" if msg.get('sender') == 'user' else "Raphael"
            content = msg.get('user_message', '') if msg.get('sender') == 'user' else msg.get('ai_response', '')
            if content:
                prompt_parts.append(f"{role}: {content}")
    
    # Add current message
    prompt_parts.append(f"\nUser: {current_message}")
    prompt_parts.append("Raphael:")
    
    return "\n".join(prompt_parts)


def parse_gemini_intent(user_message, ai_response):
    """
    Parse the user's intent from their message and AI response
    
    Args:
        user_message (str): User's message
        ai_response (str): AI's response
    
    Returns:
        dict: Intent data with action and confidence
    """
    message_lower = user_message.lower()
    
    # Intent patterns
    intent_patterns = {
        'store_memory': [
            'remember', 'store', 'save', 'keep in mind', 'note that',
            'my name is', 'i am', 'i like', 'i love', 'i hate', 'i prefer'
        ],
        'retrieve_memory': [
            'what do you know about', 'tell me about', 'recall', 'remember when',
            'what did i say about', 'remind me'
        ],
        'add_calendar_event': [
            'schedule', 'book', 'set up a meeting', 'add to calendar', 'create event',
            'appointment', 'remind me to', 'meeting at'
        ],
        'get_calendar_events': [
            'what\'s on my calendar', 'my schedule', 'what do i have today',
            'any meetings', 'events today', 'my appointments'
        ],
        'calculate': [
            'calculate', 'what is', 'what\'s', 'compute', 'solve', 'math',
            'plus', 'minus', 'times', 'divided by', '%', 'percent'
        ],
        'add_task': [
            'homework', 'assignment', 'task', 'todo', 'need to do',
            'add task', 'remind me to do', 'i have to'
        ],
        'get_tasks': [
            'my tasks', 'what do i need to do', 'pending tasks', 'homework list',
            'what\'s due', 'assignments'
        ],
        'add_expense': [
            'spent', 'bought', 'paid', 'cost', 'expense', 'purchase',
            'i spent', 'it cost', 'add expense'
        ],
        'get_budget': [
            'budget', 'spending', 'expenses', 'how much have i spent',
            'financial summary', 'money'
        ]
    }
    
    # Find matching intent
    detected_intent = 'general'
    confidence = 0.5
    
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if pattern in message_lower:
                detected_intent = intent
                confidence = 0.8
                break
        if detected_intent != 'general':
            break
    
    # Special handling for calculations
    if re.search(r'\d+\s*[\+\-\*\/\%]\s*\d+', user_message):
        detected_intent = 'calculate'
        confidence = 0.9
    
    return {
        'action': detected_intent,
        'confidence': confidence,
        'original_message': user_message
    }


def format_conversation_history(messages):
    """
    Format conversation history for Gemini context
    
    Args:
        messages (list): List of conversation messages
    
    Returns:
        list: Formatted messages for context
    """
    if not messages:
        return []
    
    formatted = []
    for msg in messages:
        if isinstance(msg, dict):
            # Handle different message formats
            if 'user_message' in msg and 'ai_response' in msg:
                formatted.append({
                    'sender': 'user',
                    'user_message': msg['user_message'],
                    'timestamp': msg.get('timestamp', '')
                })
                formatted.append({
                    'sender': 'assistant',
                    'ai_response': msg['ai_response'],
                    'timestamp': msg.get('timestamp', '')
                })
            else:
                formatted.append(msg)
    
    return formatted[-10:]  # Keep last 10 messages for context


def extract_intent_entities(message, intent_action):
    """
    Extract relevant entities from the message based on intent
    
    Args:
        message (str): User's message
        intent_action (str): Detected intent action
    
    Returns:
        dict: Extracted entities
    """
    entities = {}
    message_lower = message.lower()
    
    if intent_action == 'add_calendar_event':
        # Extract date/time patterns
        time_patterns = re.findall(r'\b\d{1,2}:\d{2}\b|\b\d{1,2}\s*(am|pm)\b', message_lower)
        if time_patterns:
            entities['time'] = time_patterns[0] if isinstance(time_patterns[0], str) else time_patterns[0][0]
        
        # Extract event title (simple heuristic)
        event_words = ['meeting', 'appointment', 'call', 'lunch', 'dinner', 'conference']
        for word in event_words:
            if word in message_lower:
                entities['title'] = word.title()
                break
    
    elif intent_action == 'add_expense':
        # Extract amount
        amount_pattern = re.search(r'\$?(\d+(?:\.\d{2})?)', message)
        if amount_pattern:
            entities['amount'] = float(amount_pattern.group(1))
        
        # Extract category (simple keywords)
        categories = ['food', 'transport', 'shopping', 'entertainment', 'bills', 'groceries']
        for category in categories:
            if category in message_lower:
                entities['category'] = category.title()
                break
    
    elif intent_action == 'add_task':
        # Extract subject
        subjects = ['math', 'english', 'science', 'history', 'homework', 'assignment']
        for subject in subjects:
            if subject in message_lower:
                entities['subject'] = subject.title()
                break
        
        # Extract due date (simple patterns)
        if 'tomorrow' in message_lower:
            entities['due_date'] = 'tomorrow'
        elif 'today' in message_lower:
            entities['due_date'] = 'today'
        elif 'next week' in message_lower:
            entities['due_date'] = 'next week'
    
    return entities
