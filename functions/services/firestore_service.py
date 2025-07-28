# Firestore service - handles all Firestore database operations
import os
from datetime import datetime
from google.cloud import firestore

# Initialize Firestore client
try:
    # Check if we're in test mode
    if os.getenv('SKIP_GOOGLE_AUTH', 'False').lower() == 'true':
        print("Running in test mode - Firestore operations will be mocked")
        db = None
    else:
        db = firestore.Client()
        print("Firestore client initialized")
except Exception as e:
    print(f"Error initializing Firestore client: {e}")
    print("Continuing with mock client for testing")
    db = None


def save_user_data(user_id, collection_name, document_id, data):
    """
    Save or update a document in user's Firestore collection.
    
    Args:
        user_id (str): Firebase user ID
        collection_name (str): Collection name ('memories', 'tasks', 'timetables', 'budgets', etc.)
        document_id (str): Document ID (if None, auto-generate)
        data (dict): Data to save
        
    Returns:
        tuple: (success: bool, document_id: str or error_message: str)
    """
    try:
        if db is None:
            print(f"Mock: Saving data for user {user_id} in {collection_name}/{document_id}: {data}")
            return True, document_id or "mock_doc_id"
        
        # Add timestamp to data
        data['updated_at'] = datetime.now().isoformat()
        
        # Create reference to user's collection
        collection_ref = db.collection('users').document(user_id).collection(collection_name)
        
        if document_id:
            # Update existing document
            doc_ref = collection_ref.document(document_id)
            doc_ref.set(data, merge=True)
            return True, document_id
        else:
            # Create new document with auto-generated ID
            doc_ref = collection_ref.document()
            doc_ref.set(data)
            return True, doc_ref.id
            
    except Exception as e:
        print(f"Error saving user data: {e}")
        return False, str(e)


def get_user_data(user_id, collection_name, document_id=None, limit=None, order_by=None, where_filters=None):
    """
    Retrieve data from user's Firestore collection.
    
    Args:
        user_id (str): Firebase user ID
        collection_name (str): Collection name
        document_id (str, optional): Specific document ID to retrieve
        limit (int, optional): Maximum number of documents to return
        order_by (tuple, optional): (field_name, direction) for ordering
        where_filters (list, optional): List of (field, operator, value) tuples for filtering
        
    Returns:
        dict or list: Document data or list of documents, None if error
    """
    try:
        if db is None:
            print(f"Mock: Getting data for user {user_id} from {collection_name}")
            if document_id:
                return {"mock_field": "mock_value", "document_id": document_id}
            else:
                return [{"mock_field": "mock_value_1"}, {"mock_field": "mock_value_2"}]
        
        collection_ref = db.collection('users').document(user_id).collection(collection_name)
        
        if document_id:
            # Get specific document
            doc = collection_ref.document(document_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        else:
            # Get multiple documents
            query = collection_ref
            
            # Apply filters
            if where_filters:
                for field, operator, value in where_filters:
                    query = query.where(field, operator, value)
            
            # Apply ordering
            if order_by:
                field_name, direction = order_by
                query = query.order_by(field_name, direction=direction)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
            
    except Exception as e:
        print(f"Error getting user data: {e}")
        return None


def delete_user_data(user_id, collection_name, document_id):
    """
    Delete a document from user's Firestore collection.
    
    Args:
        user_id (str): Firebase user ID
        collection_name (str): Collection name
        document_id (str): Document ID to delete
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if db is None:
            print(f"Mock: Deleting document {document_id} from {collection_name} for user {user_id}")
            return True, "Document deleted successfully (mock)"
        
        doc_ref = db.collection('users').document(user_id).collection(collection_name).document(document_id)
        doc_ref.delete()
        
        return True, "Document deleted successfully"
        
    except Exception as e:
        print(f"Error deleting user data: {e}")
        return False, str(e)


def batch_save_user_data(user_id, collection_name, documents):
    """
    Save multiple documents in a batch operation.
    
    Args:
        user_id (str): Firebase user ID
        collection_name (str): Collection name
        documents (list): List of dicts with 'id' (optional) and 'data' keys
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if db is None:
            print(f"Mock: Batch saving {len(documents)} documents for user {user_id} in {collection_name}")
            return True, f"Batch saved {len(documents)} documents (mock)"
        
        batch = db.batch()
        collection_ref = db.collection('users').document(user_id).collection(collection_name)
        
        for doc_info in documents:
            data = doc_info['data']
            data['updated_at'] = datetime.now().isoformat()
            
            if 'id' in doc_info and doc_info['id']:
                # Update existing document
                doc_ref = collection_ref.document(doc_info['id'])
            else:
                # Create new document
                doc_ref = collection_ref.document()
            
            batch.set(doc_ref, data, merge=True)
        
        batch.commit()
        return True, f"Batch saved {len(documents)} documents successfully"
        
    except Exception as e:
        print(f"Error in batch save: {e}")
        return False, str(e)


def search_user_data(user_id, collection_name, search_field, search_term, limit=10):
    """
    Search for documents containing a specific term in a field.
    
    Args:
        user_id (str): Firebase user ID
        collection_name (str): Collection name
        search_field (str): Field to search in
        search_term (str): Term to search for
        limit (int): Maximum number of results
        
    Returns:
        list: List of matching documents
    """
    try:
        if db is None:
            print(f"Mock: Searching for '{search_term}' in {search_field} for user {user_id}")
            return [{"mock_field": f"Contains {search_term}", "relevance": "high"}]
        
        # Note: Firestore doesn't support full-text search natively
        # This is a simple implementation that can be enhanced with
        # external search services like Algolia or Elasticsearch
        
        all_docs = get_user_data(user_id, collection_name, limit=limit*2)
        
        if not all_docs:
            return []
        
        # Simple text matching
        search_term_lower = search_term.lower()
        results = []
        
        for doc in all_docs:
            if search_field in doc and search_term_lower in str(doc[search_field]).lower():
                results.append(doc)
                if len(results) >= limit:
                    break
        
        return results
        
    except Exception as e:
        print(f"Error searching user data: {e}")
        return []


# Specific helper functions for common collections

def save_memory(user_id, memory_text, category="general"):
    """Save a memory/fact for the user."""
    data = {
        'text': memory_text,
        'category': category,
        'created_at': datetime.now().isoformat()
    }
    return save_user_data(user_id, 'memories', None, data)


def get_memories(user_id, limit=10, category=None):
    """Get user's memories, optionally filtered by category."""
    filters = None
    if category:
        filters = [('category', '==', category)]
    
    return get_user_data(
        user_id, 
        'memories', 
        limit=limit, 
        order_by=('created_at', firestore.Query.DESCENDING) if db else None,
        where_filters=filters
    )


def save_homework(user_id, subject, description, due_date):
    """Save a homework assignment."""
    data = {
        'subject': subject,
        'description': description,
        'due_date': due_date,
        'completed': False,
        'created_at': datetime.now().isoformat()
    }
    return save_user_data(user_id, 'homework', None, data)


def get_pending_homework(user_id):
    """Get pending homework assignments."""
    filters = [('completed', '==', False)]
    return get_user_data(
        user_id,
        'homework',
        where_filters=filters,
        order_by=('due_date', firestore.Query.ASCENDING) if db else None
    )


def save_budget_transaction(user_id, amount, category, transaction_type='expense', description=''):
    """Save a budget transaction."""
    data = {
        'amount': float(amount),
        'category': category,
        'type': transaction_type,  # 'expense' or 'income'
        'description': description,
        'created_at': datetime.now().isoformat()
    }
    return save_user_data(user_id, 'budget_transactions', None, data)


def get_budget_summary(user_id):
    """Get user's budget summary."""
    return get_user_data(user_id, 'budget', 'summary')


def save_timetable(user_id, day, classes):
    """Save timetable for a specific day."""
    data = {
        'classes': classes,
        'updated_at': datetime.now().isoformat()
    }
    return save_user_data(user_id, 'timetable', day.lower(), data)
