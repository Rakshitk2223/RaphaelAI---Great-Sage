# Firebase Authentication Middleware for Flask routes
import os
from functools import wraps
from flask import request, jsonify, g
import firebase_admin
from firebase_admin import credentials, auth

def firebase_auth_required(f):
    """
    Flask decorator to verify Firebase ID token and extract user information.
    
    This decorator:
    1. Expects a Firebase ID token in the request JSON body (key: 'idToken')
    2. Uses firebase_admin.auth.verify_id_token to verify the token
    3. If valid, sets g.user_id to the decoded UID and calls the original function
    4. If invalid or missing, returns a 401 Unauthorized response
    5. Handles exceptions during token verification
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get the ID token from request
            data = request.get_json()
            if not data or 'idToken' not in data:
                return jsonify({'error': 'ID token is required'}), 401
            
            id_token = data['idToken']
            
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            g.user_id = decoded_token['uid']
            g.user_email = decoded_token.get('email', '')
            g.user_name = decoded_token.get('name', '')
            
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return jsonify({'error': 'Invalid authentication token'}), 401
    
    return decorated_function


def initialize_firebase_admin():
    """
    Initialize Firebase Admin SDK.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        # Check if Firebase Admin is already initialized
        if firebase_admin._apps:
            return True
        
        # Use service account key from environment variable
        service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized with service account")
        else:
            # For Cloud Functions, use default credentials
            firebase_admin.initialize_app()
            print("Firebase Admin SDK initialized with default credentials")
        
        return True
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        return False


def get_user_claims(user_id):
    """
    Get custom claims for a user.
    
    Args:
        user_id (str): Firebase user ID
        
    Returns:
        dict: User's custom claims or empty dict if error
    """
    try:
        user_record = auth.get_user(user_id)
        return user_record.custom_claims or {}
    except Exception as e:
        print(f"Error getting user claims: {e}")
        return {}


def set_user_claims(user_id, claims):
    """
    Set custom claims for a user.
    
    Args:
        user_id (str): Firebase user ID
        claims (dict): Custom claims to set
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        auth.set_custom_user_claims(user_id, claims)
        print(f"Set custom claims for user {user_id}: {claims}")
        return True
    except Exception as e:
        print(f"Error setting user claims: {e}")
        return False
