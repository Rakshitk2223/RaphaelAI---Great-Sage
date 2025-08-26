"""
Google Calendar service for Raphael AI
Handles calendar integration and event management
"""

import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account


def get_calendar_service(user_id=None):
    """
    Get Google Calendar service object
    
    Args:
        user_id (str): User identifier (for user-specific calendar access)
    
    Returns:
        service object or None if not available
    """
    try:
        # In test mode, return None
        if os.getenv('SKIP_GOOGLE_AUTH', 'False').lower() == 'true':
            print("🔧 Calendar service not available in test mode")
            return None
        
        # Load service account credentials
        service_account_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not service_account_path or not os.path.exists(service_account_path):
            print("⚠️  Service account file not found")
            return None
        
        # Set up credentials with Calendar scope
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path, scopes=SCOPES
        )
        
        # Build the service
        service = build('calendar', 'v3', credentials=credentials)
        return service
        
    except Exception as e:
        print(f"Error setting up calendar service: {e}")
        return None


def create_google_calendar_event(service, title, date_str='today', time_str='15:00'):
    """
    Create a new Google Calendar event
    
    Args:
        service: Google Calendar service object
        title (str): Event title
        date_str (str): Date string (e.g., 'today', 'tomorrow', '2024-01-15')
        time_str (str): Time string (e.g., '15:00', '3:00 PM')
    
    Returns:
        str: Success or error message
    """
    if not service:
        return "📅 Calendar service not available"
    
    try:
        # Parse date
        event_date = parse_date_string(date_str)
        if not event_date:
            return "📅 Could not parse date. Please use format like 'today', 'tomorrow', or 'YYYY-MM-DD'"
        
        # Parse time
        event_time = parse_time_string(time_str)
        if not event_time:
            event_time = "15:00"  # Default to 3 PM
        
        # Create event datetime
        event_datetime = f"{event_date}T{event_time}:00"
        end_datetime = f"{event_date}T{add_hour_to_time(event_time)}:00"
        
        # Create event object
        event = {
            'summary': title,
            'start': {
                'dateTime': event_datetime,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'UTC',
            },
            'description': f'Event created by Raphael AI',
        }
        
        # Insert event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return f"📅 Event '{title}' created for {date_str} at {time_str}"
        
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return f"📅 Error creating event: {str(e)}"


def get_todays_events(user_id=None):
    """
    Get today's calendar events
    
    Args:
        user_id (str): User identifier
    
    Returns:
        list: List of today's events
    """
    service = get_calendar_service(user_id)
    if not service:
        return []
    
    try:
        # Get today's date range
        today = datetime.utcnow().date()
        start_time = datetime.combine(today, datetime.min.time()).isoformat() + 'Z'
        end_time = datetime.combine(today, datetime.max.time()).isoformat() + 'Z'
        
        # Call the Calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        return events
        
    except Exception as e:
        print(f"Error getting today's events: {e}")
        return []


def parse_date_string(date_str):
    """
    Parse date string into YYYY-MM-DD format
    
    Args:
        date_str (str): Date string
    
    Returns:
        str: Formatted date or None
    """
    try:
        date_str_lower = date_str.lower().strip()
        today = datetime.now().date()
        
        if date_str_lower in ['today', 'now']:
            return today.isoformat()
        elif date_str_lower == 'tomorrow':
            return (today + timedelta(days=1)).isoformat()
        elif date_str_lower == 'yesterday':
            return (today - timedelta(days=1)).isoformat()
        elif 'next week' in date_str_lower:
            return (today + timedelta(days=7)).isoformat()
        else:
            # Try to parse as ISO date
            try:
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                return parsed_date.isoformat()
            except ValueError:
                # Try other common formats
                for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt).date()
                        return parsed_date.isoformat()
                    except ValueError:
                        continue
        
        return None
        
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None


def parse_time_string(time_str):
    """
    Parse time string into HH:MM format
    
    Args:
        time_str (str): Time string
    
    Returns:
        str: Formatted time or None
    """
    try:
        time_str = time_str.strip().lower()
        
        # Handle common formats
        if 'am' in time_str or 'pm' in time_str:
            # Parse 12-hour format
            time_part = time_str.replace('am', '').replace('pm', '').strip()
            
            # Add minutes if not present
            if ':' not in time_part:
                time_part += ':00'
            
            hour, minute = map(int, time_part.split(':'))
            
            if 'pm' in time_str and hour != 12:
                hour += 12
            elif 'am' in time_str and hour == 12:
                hour = 0
            
            return f"{hour:02d}:{minute:02d}"
        
        else:
            # Assume 24-hour format
            if ':' in time_str:
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                return f"{hour:02d}:{minute:02d}"
            else:
                # Just hour
                hour = int(time_str)
                return f"{hour:02d}:00"
        
    except Exception as e:
        print(f"Error parsing time: {e}")
        return None


def add_hour_to_time(time_str):
    """
    Add one hour to a time string
    
    Args:
        time_str (str): Time in HH:MM format
    
    Returns:
        str: Time one hour later
    """
    try:
        hour, minute = map(int, time_str.split(':'))
        hour = (hour + 1) % 24
        return f"{hour:02d}:{minute:02d}"
    except:
        return "16:00"  # Default to 4 PM
