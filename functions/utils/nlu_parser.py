# NLU Parser - helper functions to interpret Gemini's NLU output
import re
import json
from datetime import datetime, timedelta


def extract_intent_from_response(gemini_response):
    """
    Extract intent information from Gemini's response.
    
    Args:
        gemini_response (str): Gemini's text response
        
    Returns:
        dict: Intent information with action type and confidence
    """
    # Look for structured intent markers in the response
    intent_patterns = {
        'store_memory': [r'remember', r'i\'ll store', r'i\'ll save', r'storing'],
        'retrieve_memory': [r'here\'s what i remember', r'i recall', r'you told me'],
        'add_calendar_event': [r'scheduling', r'i\'ll add.*event', r'creating.*appointment'],
        'get_calendar_events': [r'your schedule', r'events today', r'calendar shows'],
        'calculate': [r'the result is', r'calculation', r'equals'],
        'get_homework': [r'pending homework', r'assignments', r'homework list'],
        'add_homework': [r'i\'ll add.*homework', r'recording.*assignment'],
        'get_budget': [r'budget', r'expenses', r'spending'],
        'add_expense': [r'recorded.*expense', r'added.*expense'],
        'get_timetable': [r'classes', r'schedule', r'timetable']
    }
    
    response_lower = gemini_response.lower()
    
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if re.search(pattern, response_lower):
                return {
                    'intent': intent,
                    'confidence': 0.8,
                    'matched_pattern': pattern
                }
    
    return {
        'intent': 'general',
        'confidence': 0.5,
        'matched_pattern': None
    }


def extract_entities_from_message(message, intent_type):
    """
    Extract structured entities from user message based on intent type.
    
    Args:
        message (str): User's original message
        intent_type (str): The identified intent type
        
    Returns:
        dict: Extracted entities
    """
    entities = {}
    message_lower = message.lower()
    
    if intent_type == 'add_calendar_event':
        entities.update(extract_event_entities(message))
    elif intent_type == 'add_homework':
        entities.update(extract_homework_entities(message))
    elif intent_type == 'add_expense':
        entities.update(extract_expense_entities(message))
    elif intent_type == 'calculate':
        entities.update(extract_calculation_entities(message))
    elif intent_type == 'store_memory':
        entities['memory_text'] = message
        entities['category'] = classify_memory_category(message)
    elif intent_type == 'retrieve_memory':
        entities['query'] = extract_memory_query(message)
    
    return entities


def extract_event_entities(message):
    """Extract event-related entities from message."""
    entities = {}
    message_lower = message.lower()
    
    # Extract time
    time_patterns = [
        r'at (\d{1,2}:\d{2})',
        r'at (\d{1,2})\s*(am|pm)',
        r'(\d{1,2}:\d{2})\s*(am|pm)?',
        r'at (\d{1,2})'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, message_lower)
        if match:
            time_str = match.group(1)
            if len(match.groups()) > 1 and match.group(2):
                time_str += match.group(2)
            entities['time'] = time_str
            break
    
    # Extract date
    date_patterns = {
        'tomorrow': 1,
        'today': 0,
        'next week': 7,
        'monday': None,
        'tuesday': None,
        'wednesday': None,
        'thursday': None,
        'friday': None,
        'saturday': None,
        'sunday': None
    }
    
    for date_word, days_offset in date_patterns.items():
        if date_word in message_lower:
            entities['date'] = date_word
            if days_offset is not None:
                entities['date_offset'] = days_offset
            break
    
    # Extract event title/summary
    event_keywords = ['meeting', 'appointment', 'call', 'lunch', 'dinner', 'conference']
    for keyword in event_keywords:
        if keyword in message_lower:
            entities['event_type'] = keyword
            break
    
    # Try to extract a custom title
    title_patterns = [
        r'(?:add|schedule|create)\s+(?:a\s+)?(?:meeting|appointment|event)\s+(?:about\s+|for\s+|with\s+)?(.+?)(?:\s+at|\s+on|$)',
        r'(?:meeting|appointment|event)\s+(?:about\s+|for\s+|with\s+)?(.+?)(?:\s+at|\s+on|$)'
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, message_lower)
        if match:
            title = match.group(1).strip()
            if title and len(title) > 1:
                entities['custom_title'] = title.title()
                break
    
    return entities


def extract_homework_entities(message):
    """Extract homework-related entities from message."""
    entities = {}
    message_lower = message.lower()
    
    # Extract subject
    subjects = [
        'math', 'mathematics', 'algebra', 'calculus',
        'science', 'physics', 'chemistry', 'biology',
        'english', 'literature', 'writing',
        'history', 'geography', 'social studies',
        'art', 'music', 'pe', 'physical education'
    ]
    
    for subject in subjects:
        if subject in message_lower:
            entities['subject'] = subject.title()
            break
    
    # Extract due date
    due_patterns = {
        'tomorrow': 1,
        'today': 0,
        'next week': 7,
        'friday': None,
        'monday': None,
        'tuesday': None,
        'wednesday': None,
        'thursday': None,
        'saturday': None,
        'sunday': None
    }
    
    for due_word, days_offset in due_patterns.items():
        if due_word in message_lower:
            entities['due_date'] = due_word
            if days_offset is not None:
                entities['due_date_offset'] = days_offset
            break
    
    # Extract assignment type and description
    assignment_types = ['homework', 'assignment', 'project', 'essay', 'report', 'presentation']
    for assignment_type in assignment_types:
        if assignment_type in message_lower:
            entities['assignment_type'] = assignment_type
            # Try to extract description after the assignment type
            pattern = f'{assignment_type}\\s+(.+?)(?:\\s+due|\\s+for|$)'
            match = re.search(pattern, message_lower)
            if match:
                entities['description'] = match.group(1).strip()
            break
    
    return entities


def extract_expense_entities(message):
    """Extract expense-related entities from message."""
    entities = {}
    
    # Extract amount
    amount_patterns = [
        r'\$(\d+(?:\.\d{2})?)',
        r'(\d+(?:\.\d{2})?)\s*dollars?',
        r'(\d+(?:\.\d{2})?)\s*bucks?',
        r'spent\s+(\d+(?:\.\d{2})?)',
        r'cost\s+(\d+(?:\.\d{2})?)',
        r'paid\s+(\d+(?:\.\d{2})?)'
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, message)
        if match:
            entities['amount'] = float(match.group(1))
            break
    
    # Extract category
    categories = {
        'food': ['food', 'lunch', 'dinner', 'breakfast', 'restaurant', 'coffee', 'snack'],
        'transportation': ['gas', 'fuel', 'bus', 'taxi', 'uber', 'lyft', 'parking'],
        'entertainment': ['movie', 'concert', 'game', 'entertainment', 'fun'],
        'shopping': ['shopping', 'clothes', 'shirt', 'shoes', 'amazon'],
        'groceries': ['groceries', 'supermarket', 'store', 'walmart', 'target'],
        'utilities': ['electricity', 'water', 'internet', 'phone', 'bill'],
        'health': ['doctor', 'medicine', 'pharmacy', 'health', 'medical']
    }
    
    message_lower = message.lower()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in message_lower:
                entities['category'] = category
                break
        if 'category' in entities:
            break
    
    # Default category
    if 'category' not in entities:
        entities['category'] = 'general'
    
    # Extract description
    desc_patterns = [
        r'(?:spent|paid|bought|for)\s+(?:\$?\d+(?:\.\d{2})?\s+)?(?:on\s+)?(.+?)(?:\s+at|\s+from|$)',
        r'bought\s+(.+?)(?:\s+for|$)'
    ]
    
    for pattern in desc_patterns:
        match = re.search(pattern, message_lower)
        if match:
            desc = match.group(1).strip()
            if desc and len(desc) > 1:
                entities['description'] = desc
                break
    
    return entities


def extract_calculation_entities(message):
    """Extract calculation-related entities from message."""
    entities = {}
    
    # Extract mathematical expression
    # Look for basic mathematical operations
    math_pattern = r'([\d\+\-\*\/\(\)\.\s]+)'
    matches = re.findall(math_pattern, message)
    
    if matches:
        # Take the longest match as the expression
        expression = max(matches, key=len).strip()
        # Clean up the expression
        expression = re.sub(r'[^\d\+\-\*\/\(\)\.\s]', '', expression)
        if expression:
            entities['expression'] = expression
    
    # Also look for word-based math
    word_math_patterns = [
        r'what\s+is\s+(.+?)(?:\s*\?|$)',
        r'calculate\s+(.+?)(?:\s*\?|$)',
        r'solve\s+(.+?)(?:\s*\?|$)'
    ]
    
    for pattern in word_math_patterns:
        match = re.search(pattern, message.lower())
        if match:
            entities['word_expression'] = match.group(1).strip()
            break
    
    return entities


def classify_memory_category(memory_text):
    """Classify memory into categories for better organization."""
    text_lower = memory_text.lower()
    
    # Personal information
    if any(word in text_lower for word in ['my name', 'i am', 'i\'m called', 'call me']):
        return 'personal_info'
    
    # Preferences
    if any(word in text_lower for word in ['i like', 'i love', 'i prefer', 'my favorite']):
        return 'preferences'
    
    # Goals and aspirations
    if any(word in text_lower for word in ['i want to', 'my goal', 'i hope', 'i plan']):
        return 'goals'
    
    # Important dates
    if any(word in text_lower for word in ['birthday', 'anniversary', 'important date']):
        return 'important_dates'
    
    # Contacts and relationships
    if any(word in text_lower for word in ['my friend', 'my family', 'contact', 'phone number']):
        return 'contacts'
    
    # Work/school related
    if any(word in text_lower for word in ['work', 'job', 'school', 'class', 'teacher', 'boss']):
        return 'work_school'
    
    return 'general'


def extract_memory_query(message):
    """Extract the query term from memory retrieval requests."""
    query_patterns = [
        r'what do you know about (.+?)(?:\?|$)',
        r'tell me about (.+?)(?:\?|$)',
        r'do you remember (.+?)(?:\?|$)',
        r'what did i tell you about (.+?)(?:\?|$)',
        r'recall (.+?)(?:\?|$)'
    ]
    
    message_lower = message.lower()
    for pattern in query_patterns:
        match = re.search(pattern, message_lower)
        if match:
            return match.group(1).strip()
    
    # If no specific pattern matches, return the whole message as query
    return message


def parse_natural_date(date_string):
    """
    Parse natural language date strings into datetime objects.
    
    Args:
        date_string (str): Natural language date string
        
    Returns:
        datetime: Parsed datetime object or None
    """
    if not date_string:
        return None
    
    date_string = date_string.lower().strip()
    now = datetime.now()
    
    # Relative dates
    if date_string in ['today']:
        return now.replace(hour=12, minute=0, second=0, microsecond=0)
    elif date_string in ['tomorrow']:
        return now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)
    elif date_string in ['yesterday']:
        return now.replace(hour=12, minute=0, second=0, microsecond=0) - timedelta(days=1)
    elif date_string in ['next week']:
        return now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=7)
    elif date_string in ['last week']:
        return now.replace(hour=12, minute=0, second=0, microsecond=0) - timedelta(days=7)
    
    # Weekdays
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    if date_string in weekdays:
        target_weekday = weekdays[date_string]
        current_weekday = now.weekday()
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
    
    return None


def parse_natural_time(time_string):
    """
    Parse natural language time strings.
    
    Args:
        time_string (str): Natural language time string
        
    Returns:
        tuple: (hour, minute) or None
    """
    if not time_string:
        return None
    
    time_string = time_string.lower().strip()
    
    # Named times
    named_times = {
        'morning': (9, 0),
        'afternoon': (14, 0),
        'evening': (18, 0),
        'night': (20, 0),
        'noon': (12, 0),
        'midnight': (0, 0)
    }
    
    if time_string in named_times:
        return named_times[time_string]
    
    # Parse time patterns
    time_patterns = [
        r'(\d{1,2}):(\d{2})\s*(am|pm)?',
        r'(\d{1,2})\s*(am|pm)',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, time_string)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
            
            # Handle am/pm
            if len(match.groups()) > 2 and match.group(3):
                if match.group(3) == 'pm' and hour != 12:
                    hour += 12
                elif match.group(3) == 'am' and hour == 12:
                    hour = 0
            
            return (hour, minute)
    
    return None


def validate_entities(entities, entity_type):
    """
    Validate extracted entities for completeness and correctness.
    
    Args:
        entities (dict): Extracted entities
        entity_type (str): Type of entities (event, homework, expense, etc.)
        
    Returns:
        tuple: (is_valid: bool, missing_fields: list, corrected_entities: dict)
    """
    missing_fields = []
    corrected_entities = entities.copy()
    
    if entity_type == 'event':
        # Events need at least a title and time
        if 'custom_title' not in entities and 'event_type' not in entities:
            missing_fields.append('title')
        if 'time' not in entities:
            missing_fields.append('time')
        if 'date' not in entities:
            corrected_entities['date'] = 'today'  # Default to today
    
    elif entity_type == 'homework':
        # Homework needs subject and description
        if 'subject' not in entities:
            missing_fields.append('subject')
        if 'description' not in entities and 'assignment_type' not in entities:
            missing_fields.append('description')
        if 'due_date' not in entities:
            corrected_entities['due_date'] = 'next week'  # Default
    
    elif entity_type == 'expense':
        # Expenses need amount
        if 'amount' not in entities:
            missing_fields.append('amount')
        if 'category' not in entities:
            corrected_entities['category'] = 'general'  # Default
    
    is_valid = len(missing_fields) == 0
    return is_valid, missing_fields, corrected_entities
