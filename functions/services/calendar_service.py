# Google Calendar service - handles all Google Calendar API operations
import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service(user_id):
    """
    Get an authorized Google Calendar service instance for the given user_id.
    
    Note: This is a simplified implementation using service account credentials.
    In production, you would need to implement proper OAuth flow for each user
    and store their refresh tokens securely in Firestore.
    
    Args:
        user_id (str): Firebase user ID
        
    Returns:
        googleapiclient.discovery.Resource: Calendar service instance or None
    """
    try:
        # Check if we're in test mode
        if os.getenv('SKIP_GOOGLE_AUTH', 'False').lower() == 'true':
            print(f"Mock: Getting calendar service for user {user_id}")
            return None
        
        # For development/testing, use service account credentials
        service_account_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if service_account_path and os.path.exists(service_account_path):
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path, scopes=SCOPES)
            service = build('calendar', 'v3', credentials=credentials)
            return service
        
        print(f"No calendar credentials found for user {user_id}")
        return None
        
    except Exception as e:
        print(f"Error setting up calendar service: {e}")
        return None


def create_google_calendar_event(service, summary, start_datetime, end_datetime=None, description=None):
    """
    Create an event in Google Calendar.
    
    Args:
        service: Google Calendar service instance
        summary (str): Event title/summary
        start_datetime (datetime): Event start time
        end_datetime (datetime, optional): Event end time (defaults to 1 hour after start)
        description (str, optional): Event description
        
    Returns:
        tuple: (success: bool, result: dict or error_message: str)
    """
    try:
        if service is None:
            # Mock implementation for testing
            print(f"Mock: Creating calendar event '{summary}' at {start_datetime}")
            return True, {
                'id': 'mock_event_id',
                'summary': summary,
                'start': start_datetime.isoformat(),
                'htmlLink': 'https://calendar.google.com/mock_link'
            }
        
        if not end_datetime:
            end_datetime = start_datetime + timedelta(hours=1)
        
        # Get user's timezone preference (default to UTC)
        timezone = 'UTC'  # This could be retrieved from user preferences
        
        event = {
            'summary': summary,
            'description': description or '',
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': timezone,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 30},       # 30 minutes before
                ],
            },
        }
        
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        
        return True, {
            'id': event_result.get('id'),
            'summary': event_result.get('summary'),
            'start': event_result['start'].get('dateTime', event_result['start'].get('date')),
            'htmlLink': event_result.get('htmlLink')
        }
        
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return False, str(e)


def get_google_calendar_events(service, start_datetime, end_datetime):
    """
    Retrieve events from Google Calendar within a date range.
    
    Args:
        service: Google Calendar service instance
        start_datetime (datetime): Start of date range
        end_datetime (datetime): End of date range
        
    Returns:
        list: List of event dictionaries or empty list if error
    """
    try:
        if service is None:
            # Mock implementation for testing
            print(f"Mock: Getting calendar events from {start_datetime} to {end_datetime}")
            return [
                {
                    'id': 'mock_event_1',
                    'summary': 'Team meeting',
                    'start': start_datetime.replace(hour=9, minute=0).isoformat(),
                    'end': start_datetime.replace(hour=10, minute=0).isoformat()
                },
                {
                    'id': 'mock_event_2',
                    'summary': 'Lunch with client',
                    'start': start_datetime.replace(hour=12, minute=0).isoformat(),
                    'end': start_datetime.replace(hour=13, minute=0).isoformat()
                }
            ]
        
        # Convert datetime objects to RFC3339 format for API
        time_min = start_datetime.isoformat() + 'Z'
        time_max = end_datetime.isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format events for easier consumption
        formatted_events = []
        for event in events:
            formatted_events.append({
                'id': event.get('id'),
                'summary': event.get('summary', 'No title'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'htmlLink': event.get('htmlLink', '')
            })
        
        return formatted_events
        
    except Exception as e:
        print(f"Error getting calendar events: {e}")
        return []


def get_todays_events(service):
    """
    Get today's calendar events.
    
    Args:
        service: Google Calendar service instance
        
    Returns:
        list: List of today's events
    """
    today = datetime.now().date()
    start_time = datetime.combine(today, datetime.min.time())
    end_time = datetime.combine(today, datetime.max.time())
    
    return get_google_calendar_events(service, start_time, end_time)


def get_upcoming_events(service, days_ahead=7):
    """
    Get upcoming events for the next specified number of days.
    
    Args:
        service: Google Calendar service instance
        days_ahead (int): Number of days to look ahead
        
    Returns:
        list: List of upcoming events
    """
    start_time = datetime.now()
    end_time = start_time + timedelta(days=days_ahead)
    
    return get_google_calendar_events(service, start_time, end_time)


def update_google_calendar_event(service, event_id, updates):
    """
    Update an existing calendar event.
    
    Args:
        service: Google Calendar service instance
        event_id (str): ID of the event to update
        updates (dict): Dictionary of fields to update
        
    Returns:
        tuple: (success: bool, result: dict or error_message: str)
    """
    try:
        if service is None:
            print(f"Mock: Updating calendar event {event_id} with {updates}")
            return True, {"id": event_id, "updated": True}
        
        # Get the existing event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update the fields
        for key, value in updates.items():
            if key in ['summary', 'description', 'location']:
                event[key] = value
            elif key == 'start_datetime':
                event['start']['dateTime'] = value.isoformat()
            elif key == 'end_datetime':
                event['end']['dateTime'] = value.isoformat()
        
        # Update the event
        updated_event = service.events().update(
            calendarId='primary', 
            eventId=event_id, 
            body=event
        ).execute()
        
        return True, {
            'id': updated_event.get('id'),
            'summary': updated_event.get('summary'),
            'start': updated_event['start'].get('dateTime', updated_event['start'].get('date')),
            'htmlLink': updated_event.get('htmlLink')
        }
        
    except Exception as e:
        print(f"Error updating calendar event: {e}")
        return False, str(e)


def delete_google_calendar_event(service, event_id):
    """
    Delete a calendar event.
    
    Args:
        service: Google Calendar service instance
        event_id (str): ID of the event to delete
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if service is None:
            print(f"Mock: Deleting calendar event {event_id}")
            return True, "Event deleted successfully (mock)"
        
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True, "Event deleted successfully"
        
    except Exception as e:
        print(f"Error deleting calendar event: {e}")
        return False, str(e)


def search_calendar_events(service, query, max_results=10):
    """
    Search for calendar events by text query.
    
    Args:
        service: Google Calendar service instance
        query (str): Search query
        max_results (int): Maximum number of results
        
    Returns:
        list: List of matching events
    """
    try:
        if service is None:
            print(f"Mock: Searching calendar events for '{query}'")
            return [{"summary": f"Mock event matching '{query}'", "start": datetime.now().isoformat()}]
        
        # Search in the next 30 days
        start_time = datetime.now()
        end_time = start_time + timedelta(days=30)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime',
            q=query,  # Search query
            maxResults=max_results
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format events
        formatted_events = []
        for event in events:
            formatted_events.append({
                'id': event.get('id'),
                'summary': event.get('summary', 'No title'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'description': event.get('description', ''),
                'htmlLink': event.get('htmlLink', '')
            })
        
        return formatted_events
        
    except Exception as e:
        print(f"Error searching calendar events: {e}")
        return []


# Helper functions for date/time parsing

def parse_relative_date(date_string):
    """
    Parse relative date strings like 'tomorrow', 'next week', etc.
    
    Args:
        date_string (str): Relative date string
        
    Returns:
        datetime: Parsed datetime object
    """
    now = datetime.now()
    date_string = date_string.lower().strip()
    
    if date_string in ['today']:
        return now.replace(hour=12, minute=0, second=0, microsecond=0)
    elif date_string in ['tomorrow']:
        return now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)
    elif date_string in ['next week']:
        return now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=7)
    elif date_string in ['next month']:
        return now.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=30)
    else:
        # Default to today if not recognized
        return now.replace(hour=12, minute=0, second=0, microsecond=0)


def parse_time_string(time_string):
    """
    Parse time strings like '3pm', '15:30', etc.
    
    Args:
        time_string (str): Time string
        
    Returns:
        tuple: (hour, minute) or None if parsing fails
    """
    import re
    
    time_string = time_string.lower().strip()
    
    # Try to match patterns like "3pm", "3:30pm", "15:30"
    patterns = [
        r'(\d{1,2}):(\d{2})\s*(am|pm)?',
        r'(\d{1,2})\s*(am|pm)',
        r'(\d{1,2}):(\d{2})',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, time_string)
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
