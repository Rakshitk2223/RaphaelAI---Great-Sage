"""
Authentication middleware for Raphael AI
Handles Firebase ID token verification and user authentication
"""

import os
import json
from functools import wraps
from flask import request, jsonify, g
import firebase_admin
from firebase_admin import credentials, auth


def initialize_firebase_admin():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        try:
            # Try to load service account from environment variable
            service_account_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            
            if service_account_path and os.path.exists(service_account_path):
                # Use service account file
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase Admin initialized with service account")
            else:
                # Use default credentials (for production/Cloud Functions)
                firebase_admin.initialize_app()
                print("✅ Firebase Admin initialized with default credentials")
                
        except Exception as e:
            print(f"⚠️  Firebase Admin initialization error: {e}")
            # For local development without proper credentials
            if os.environ.get('SKIP_GOOGLE_AUTH') == 'True':
                print("🔧 Running in local development mode without Firebase Auth")
            else:
                raise e


def firebase_auth_required(f):
    """
    Decorator that requires Firebase authentication.
    Extracts user ID from Firebase ID token and stores in g.user_id
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication in local development mode
        if os.environ.get('SKIP_GOOGLE_AUTH') == 'True':
            g.user_id = 'test_user_123'  # Use test user ID
            return f(*args, **kwargs)
        
        try:
            # Get the ID token from request
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No request data provided'}), 400
            
            id_token = data.get('idToken')
            if not id_token:
                return jsonify({'error': 'No ID token provided'}), 401
            
            # Verify the ID token
            try:
                decoded_token = auth.verify_id_token(id_token)
                user_id = decoded_token['uid']
                g.user_id = user_id
                
                return f(*args, **kwargs)
                
            except auth.InvalidIdTokenError:
                return jsonify({'error': 'Invalid ID token'}), 401
            except auth.ExpiredIdTokenError:
                return jsonify({'error': 'Expired ID token'}), 401
            except Exception as e:
                print(f"Token verification error: {e}")
                return jsonify({'error': 'Authentication failed'}), 401
                
        except Exception as e:
            print(f"Authentication middleware error: {e}")
            return jsonify({'error': 'Internal authentication error'}), 500
    
    return decorated_function


def get_current_user_id():
    """Get the current authenticated user ID"""
    return getattr(g, 'user_id', None)
