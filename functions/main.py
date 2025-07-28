import os
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from dotenv import load_dotenv

# Import our refactored services
from utils.auth_middleware import firebase_auth_required, initialize_firebase_admin
from services.firestore_service import (
    save_memory, get_memories, save_homework, get_pending_homework,
    save_budget_transaction, get_budget_summary, save_user_data, get_user_data
)
from services.gemini_service import (
    get_gemini_response, parse_gemini_intent, format_conversation_history
)
from services.calendar_service import (
    get_calendar_service, create_google_calendar_event, get_todays_events
)
from utils.calculations import safe_calculate, calculate_budget_summary
from utils.nlu_parser import extract_entities_from_message

# Load environment variables for local development
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Firebase Admin SDK
initialize_firebase_admin()

print("Raphael AI backend initialized successfully!")


@app.route('/chat', methods=['POST'])
@firebase_auth_required
def chat():
    """Main chat endpoint - orchestrates the AI conversation flow."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        user_id = g.user_id
        
        # Get user's recent conversation history and context
        recent_messages = get_user_data(user_id, 'conversations', limit=6)
        memories = get_memories(user_id, limit=5)
        budget_info = get_budget_summary(user_id)
        homework = get_pending_homework(user_id)
        
        # Format context for Gemini
        user_personal_context = {
            'memories': [m.get('text', '') for m in (memories or [])],
            'budget': format_budget_context(budget_info),
            'homework': [f"{h.get('subject', '')}: {h.get('description', '')}" for h in (homework or [])],
        }
        
        conversation_history = format_conversation_history(recent_messages or [])
        
        # Get response from Gemini with full context
        gemini_response = get_gemini_response(
            message, 
            conversation_history, 
            user_personal_context
        )
        
        # Parse intent and extract entities
        intent_data = parse_gemini_intent(message, gemini_response)
        entities = extract_entities_from_message(message, intent_data.get('action', 'general'))
        
        # Execute specific actions based on intent
        action_result = execute_action(user_id, intent_data, entities, message)
        
        # Combine Gemini response with action result
        final_response = gemini_response + action_result
        
        # Store conversation history
        conversation_data = {
            'user_message': message,
            'ai_response': final_response,
            'intent': intent_data.get('action', 'general'),
            'timestamp': datetime.now().isoformat()
        }
        save_user_data(user_id, 'conversations', None, conversation_data)
        
        return jsonify({
            'message': final_response,
            'user_id': user_id,
            'intent': intent_data.get('action', 'general')
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/user-data', methods=['GET'])
@firebase_auth_required
def get_user_data_summary():
    """Get user's personal data summary."""
    try:
        user_id = g.user_id
        
        memories = get_memories(user_id, limit=10)
        homework = get_pending_homework(user_id)
        budget = get_budget_summary(user_id)
        
        return jsonify({
            'user_id': user_id,
            'memories_count': len(memories or []),
            'recent_memories': [m.get('text', '') for m in (memories or [])[:5]],
            'homework_count': len(homework or []),
            'budget': format_budget_context(budget)
        })
        
    except Exception as e:
        print(f"Error getting user data: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


def execute_action(user_id, intent_data, entities, message):
    """Execute specific actions based on intent."""
    action_result = ""
    action = intent_data.get('action')
    
    if action == 'store_memory':
        success, _ = save_memory(user_id, message)
        if success:
            action_result = "\n✅ I've stored this information in my memory."
    
    elif action == 'retrieve_memory':
        query = entities.get('query', message)
        memories = get_memories(user_id, limit=10)
        if memories:
            relevant_memories = [m for m in memories if query.lower() in m.get('text', '').lower()]
            if relevant_memories:
                memory_texts = [m.get('text', '') for m in relevant_memories[:3]]
                action_result = f"\n📝 Here's what I remember: {'; '.join(memory_texts)}"
    
    elif action == 'add_calendar_event':
        try:
            service = get_calendar_service(user_id)
            if service:
                event_result = create_google_calendar_event(
                    service, 
                    entities.get('custom_title', 'Event'),
                    entities.get('date', 'today'),
                    entities.get('time', '15:00')
                )
                action_result = event_result
            else:
                action_result = "\n📅 Calendar service not available. Please check your credentials."
        except Exception as e:
            action_result = f"\n📅 Error creating calendar event: {str(e)}"
    
    elif action == 'get_calendar_events':
        try:
            events = get_todays_events(user_id)
            if events:
                event_list = [f"• {event.get('summary', 'Untitled')} at {event.get('start', {}).get('dateTime', 'No time')}" for event in events[:5]]
                action_result = f"\n📅 Today's events:\n{chr(10).join(event_list)}"
            else:
                action_result = "\n📅 No events scheduled for today."
        except Exception as e:
            action_result = f"\n📅 Error retrieving calendar events: {str(e)}"
    
    elif action == 'calculate':
        expression = entities.get('expression', message)
        success, result = safe_calculate(expression)
        if success:
            action_result = f"\n🔢 The result is: {result}"
        else:
            action_result = f"\n🔢 {result}"
    
    elif action == 'add_homework':
        try:
            subject = entities.get('subject', 'General')
            description = entities.get('description', message)
            due_date = entities.get('due_date', 'No due date')
            
            success, _ = save_homework(user_id, subject, description, due_date)
            if success:
                action_result = f"\n📚 Added homework for {subject}: {description}"
            else:
                action_result = "\n📚 Error adding homework. Please try again."
        except Exception as e:
            action_result = f"\n📚 Error adding homework: {str(e)}"
    
    elif action == 'get_homework':
        homework_list = get_pending_homework(user_id)
        if homework_list:
            hw_items = [f"• {hw.get('subject', 'No subject')}: {hw.get('description', 'No description')}" for hw in homework_list[:5]]
            action_result = f"\n📚 Pending homework:\n{chr(10).join(hw_items)}"
        else:
            action_result = "\n📚 No pending homework found."
    
    elif action == 'add_expense':
        try:
            amount = entities.get('amount', 0)
            category = entities.get('category', 'Other')
            description = entities.get('description', message)
            
            success, _ = save_budget_transaction(user_id, amount, category, description, 'expense')
            if success:
                action_result = f"\n💰 Added expense: ${amount} for {category}"
            else:
                action_result = "\n💰 Error adding expense. Please try again."
        except Exception as e:
            action_result = f"\n💰 Error adding expense: {str(e)}"
    
    elif action == 'get_budget':
        budget_info = get_budget_summary(user_id)
        if budget_info:
            action_result = f"\n💰 Budget summary: {format_budget_context(budget_info)}"
        else:
            action_result = "\n💰 No budget data found."
    
    return action_result


def format_budget_context(budget_info):
    """Format budget information for context."""
    if not budget_info:
        return "No budget information available"
    
    total_income = budget_info.get('total_income', 0)
    total_expenses = budget_info.get('total_expenses', 0)
    balance = total_income - total_expenses
    
    return f"Income: ${total_income}, Expenses: ${total_expenses}, Balance: ${balance}"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
