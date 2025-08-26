"""
Calculation utilities for Raphael AI
Handles mathematical calculations and entity extraction
"""

import re
import ast
import operator
from datetime import datetime


def safe_calculate(expression):
    """
    Safely evaluate mathematical expressions
    
    Args:
        expression (str): Mathematical expression to evaluate
    
    Returns:
        tuple: (success: bool, result: str/float)
    """
    try:
        # Clean the expression
        expression = expression.strip()
        
        # Replace common words with operators
        replacements = {
            'plus': '+',
            'add': '+',
            'minus': '-',
            'subtract': '-',
            'times': '*',
            'multiply': '*',
            'multiplied by': '*',
            'divided by': '/',
            'divide': '/',
            'percent of': '* 0.01 *',
            '%': '* 0.01',
            'of': '*'
        }
        
        expression_lower = expression.lower()
        for word, symbol in replacements.items():
            expression_lower = expression_lower.replace(word, symbol)
        
        # Extract numbers and operators
        # Allow basic mathematical operations only
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression_lower.replace(' ', '')):
            return False, "Invalid characters in expression"
        
        # Use AST to safely evaluate
        result = safe_eval(expression_lower)
        
        if result is not None:
            # Format the result nicely
            if isinstance(result, float):
                if result.is_integer():
                    return True, int(result)
                else:
                    return True, round(result, 2)
            return True, result
        else:
            return False, "Could not evaluate expression"
            
    except Exception as e:
        return False, f"Calculation error: {str(e)}"


def safe_eval(expression):
    """
    Safely evaluate a mathematical expression using AST
    
    Args:
        expression (str): Expression to evaluate
    
    Returns:
        float/int: Result of calculation or None if invalid
    """
    try:
        # Parse the expression into an AST
        node = ast.parse(expression, mode='eval')
        
        # Define allowed operations
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        def _eval(node):
            if isinstance(node, ast.Num):  # Numbers
                return node.n
            elif isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.BinOp):  # Binary operations
                left = _eval(node.left)
                right = _eval(node.right)
                op = allowed_operators.get(type(node.op))
                if op:
                    return op(left, right)
                else:
                    raise ValueError(f"Unsupported operation: {type(node.op)}")
            elif isinstance(node, ast.UnaryOp):  # Unary operations
                operand = _eval(node.operand)
                op = allowed_operators.get(type(node.op))
                if op:
                    return op(operand)
                else:
                    raise ValueError(f"Unsupported unary operation: {type(node.op)}")
            else:
                raise ValueError(f"Unsupported node type: {type(node)}")
        
        return _eval(node.body)
        
    except Exception as e:
        print(f"Safe eval error: {e}")
        return None


def extract_entities_from_message(message, intent_action):
    """
    Extract relevant entities from user message based on intent
    
    Args:
        message (str): User's message
        intent_action (str): Detected intent
    
    Returns:
        dict: Extracted entities
    """
    entities = {}
    message_lower = message.lower()
    
    try:
        if intent_action == 'calculate':
            # Extract mathematical expression
            # Look for numbers and operators
            math_pattern = r'[\d\+\-\*\/\.\(\)\s]+'
            matches = re.findall(math_pattern, message)
            if matches:
                # Find the longest match (most likely the full expression)
                expression = max(matches, key=len).strip()
                entities['expression'] = expression
        
        elif intent_action == 'add_expense':
            # Extract amount
            amount_patterns = [
                r'\$(\d+(?:\.\d{2})?)',  # $123.45
                r'(\d+(?:\.\d{2})?)\s*dollars?',  # 123.45 dollars
                r'spent\s+(\d+(?:\.\d{2})?)',  # spent 123.45
                r'cost\s+(\d+(?:\.\d{2})?)',  # cost 123.45
            ]
            
            for pattern in amount_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    entities['amount'] = float(match.group(1))
                    break
            
            # Extract category
            categories = {
                'food': ['food', 'lunch', 'dinner', 'breakfast', 'restaurant', 'groceries'],
                'transport': ['uber', 'taxi', 'bus', 'train', 'gas', 'fuel'],
                'shopping': ['shopping', 'clothes', 'amazon', 'store'],
                'entertainment': ['movie', 'netflix', 'spotify', 'game'],
                'bills': ['bill', 'electricity', 'internet', 'phone'],
                'health': ['doctor', 'medicine', 'pharmacy', 'hospital']
            }
            
            for category, keywords in categories.items():
                if any(keyword in message_lower for keyword in keywords):
                    entities['category'] = category.title()
                    break
        
        elif intent_action == 'add_task':
            # Extract subject
            subjects = {
                'math': ['math', 'mathematics', 'algebra', 'geometry', 'calculus'],
                'english': ['english', 'literature', 'writing', 'essay'],
                'science': ['science', 'physics', 'chemistry', 'biology'],
                'history': ['history', 'social studies'],
                'computer': ['computer', 'programming', 'coding', 'cs']
            }
            
            for subject, keywords in subjects.items():
                if any(keyword in message_lower for keyword in keywords):
                    entities['subject'] = subject.title()
                    break
            
            # Extract due date
            if 'tomorrow' in message_lower:
                entities['due_date'] = 'tomorrow'
            elif 'today' in message_lower:
                entities['due_date'] = 'today'
            elif 'next week' in message_lower:
                entities['due_date'] = 'next week'
            elif 'monday' in message_lower:
                entities['due_date'] = 'monday'
            elif 'friday' in message_lower:
                entities['due_date'] = 'friday'
        
        elif intent_action == 'add_calendar_event':
            # Extract time
            time_patterns = [
                r'\b(\d{1,2}:\d{2})\b',  # 14:30
                r'\b(\d{1,2})\s*(am|pm)\b',  # 3 PM
                r'\b(\d{1,2}:\d{2})\s*(am|pm)\b',  # 3:30 PM
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    entities['time'] = match.group(1) if len(match.groups()) == 1 else f"{match.group(1)} {match.group(2)}"
                    break
            
            # Extract date
            if 'tomorrow' in message_lower:
                entities['date'] = 'tomorrow'
            elif 'today' in message_lower:
                entities['date'] = 'today'
            elif 'next week' in message_lower:
                entities['date'] = 'next week'
            
            # Extract event type/title
            event_types = ['meeting', 'appointment', 'call', 'lunch', 'dinner', 'conference']
            for event_type in event_types:
                if event_type in message_lower:
                    entities['title'] = event_type.title()
                    break
    
    except Exception as e:
        print(f"Error extracting entities: {e}")
    
    return entities


def format_number(number):
    """
    Format a number for display
    
    Args:
        number (float/int): Number to format
    
    Returns:
        str: Formatted number
    """
    try:
        if isinstance(number, float):
            if number.is_integer():
                return str(int(number))
            else:
                return f"{number:.2f}"
        return str(number)
    except:
        return str(number)


def extract_percentage_calculation(message):
    """
    Extract percentage calculations from message
    
    Args:
        message (str): User message
    
    Returns:
        dict: Percentage calculation details
    """
    try:
        # Patterns for percentage calculations
        patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)',  # 15% of 200
            r'what\s+is\s+(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)',  # what is 15% of 200
            r'(\d+(?:\.\d+)?)\s*percent\s*of\s*(\d+(?:\.\d+)?)',  # 15 percent of 200
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                percentage = float(match.group(1))
                base_number = float(match.group(2))
                result = (percentage / 100) * base_number
                
                return {
                    'percentage': percentage,
                    'base': base_number,
                    'result': result,
                    'expression': f"{percentage}% of {base_number} = {result}"
                }
        
        return {}
        
    except Exception as e:
        print(f"Error extracting percentage: {e}")
        return {}
