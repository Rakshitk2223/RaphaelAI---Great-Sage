# Calculations utility - specific logic for budget calculations and other math operations
import re
import operator
from datetime import datetime, timedelta


def safe_calculate(expression):
    """
    Safely perform basic mathematical calculations.
    
    Args:
        expression (str): Mathematical expression to evaluate
        
    Returns:
        tuple: (success: bool, result: float or error_message: str)
    """
    try:
        # Remove any non-mathematical characters for safety
        clean_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        
        # Additional safety checks
        if len(clean_expr) > 100:
            return False, "Expression too complex"
        
        if not clean_expr.strip():
            return False, "No valid mathematical expression found"
        
        # Check for dangerous patterns
        dangerous_patterns = ['__', 'import', 'exec', 'eval', 'open', 'file']
        for pattern in dangerous_patterns:
            if pattern in expression.lower():
                return False, "Invalid expression"
        
        # Evaluate the expression
        result = eval(clean_expr)
        
        # Check if result is a number
        if isinstance(result, (int, float)):
            return True, float(result)
        else:
            return False, "Result is not a number"
            
    except ZeroDivisionError:
        return False, "Division by zero is not allowed"
    except Exception as e:
        return False, f"Calculation error: {str(e)}"


def calculate_budget_summary(transactions, monthly_budget=None):
    """
    Calculate budget summary from a list of transactions.
    
    Args:
        transactions (list): List of transaction dictionaries
        monthly_budget (float, optional): Monthly budget limit
        
    Returns:
        dict: Budget summary with totals and analysis
    """
    try:
        summary = {
            'total_income': 0.0,
            'total_expenses': 0.0,
            'net_amount': 0.0,
            'monthly_budget': monthly_budget or 0.0,
            'remaining_budget': 0.0,
            'categories': {},
            'transaction_count': len(transactions),
            'analysis': {}
        }
        
        # Process each transaction
        for transaction in transactions:
            amount = float(transaction.get('amount', 0))
            transaction_type = transaction.get('type', 'expense')
            category = transaction.get('category', 'uncategorized')
            
            if transaction_type == 'income':
                summary['total_income'] += amount
            else:  # expense
                summary['total_expenses'] += amount
                
                # Categorize expenses
                if category not in summary['categories']:
                    summary['categories'][category] = {
                        'total': 0.0,
                        'count': 0,
                        'percentage': 0.0
                    }
                
                summary['categories'][category]['total'] += amount
                summary['categories'][category]['count'] += 1
        
        # Calculate derived values
        summary['net_amount'] = summary['total_income'] - summary['total_expenses']
        
        if monthly_budget:
            summary['remaining_budget'] = monthly_budget - summary['total_expenses']
            summary['budget_used_percentage'] = (summary['total_expenses'] / monthly_budget) * 100
        
        # Calculate category percentages
        if summary['total_expenses'] > 0:
            for category in summary['categories']:
                cat_total = summary['categories'][category]['total']
                summary['categories'][category]['percentage'] = (cat_total / summary['total_expenses']) * 100
        
        # Generate analysis
        summary['analysis'] = generate_budget_analysis(summary)
        
        return summary
        
    except Exception as e:
        print(f"Error calculating budget summary: {e}")
        return None


def generate_budget_analysis(budget_summary):
    """
    Generate insights and recommendations based on budget data.
    
    Args:
        budget_summary (dict): Budget summary data
        
    Returns:
        dict: Analysis insights and recommendations
    """
    analysis = {
        'status': 'good',
        'alerts': [],
        'recommendations': [],
        'insights': []
    }
    
    try:
        monthly_budget = budget_summary.get('monthly_budget', 0)
        total_expenses = budget_summary.get('total_expenses', 0)
        remaining_budget = budget_summary.get('remaining_budget', 0)
        categories = budget_summary.get('categories', {})
        
        # Budget status analysis
        if monthly_budget > 0:
            usage_percentage = (total_expenses / monthly_budget) * 100
            
            if usage_percentage > 100:
                analysis['status'] = 'over_budget'
                analysis['alerts'].append(f"You've exceeded your monthly budget by ${total_expenses - monthly_budget:.2f}")
            elif usage_percentage > 80:
                analysis['status'] = 'warning'
                analysis['alerts'].append(f"You've used {usage_percentage:.1f}% of your monthly budget")
            elif usage_percentage > 50:
                analysis['status'] = 'moderate'
                analysis['insights'].append(f"You've used {usage_percentage:.1f}% of your monthly budget")
            else:
                analysis['status'] = 'good'
                analysis['insights'].append(f"You're doing well! Only {usage_percentage:.1f}% of budget used")
        
        # Category analysis
        if categories:
            # Find top spending categories
            sorted_categories = sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True)
            
            if sorted_categories:
                top_category, top_data = sorted_categories[0]
                analysis['insights'].append(f"Your top spending category is {top_category} (${top_data['total']:.2f})")
                
                # Check for high percentage in single category
                if top_data['percentage'] > 50:
                    analysis['recommendations'].append(f"Consider reducing {top_category} expenses (currently {top_data['percentage']:.1f}% of total)")
        
        # Spending pattern insights
        if total_expenses > 0:
            daily_average = total_expenses / 30  # Assume monthly data
            analysis['insights'].append(f"Average daily spending: ${daily_average:.2f}")
            
            if monthly_budget > 0:
                recommended_daily = monthly_budget / 30
                if daily_average > recommended_daily:
                    analysis['recommendations'].append(f"Try to limit daily spending to ${recommended_daily:.2f} to stay within budget")
        
        # Recommendations based on remaining budget
        if remaining_budget > 0:
            days_remaining = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - datetime.now()
            daily_allowance = remaining_budget / max(days_remaining.days, 1)
            analysis['recommendations'].append(f"Daily allowance for rest of month: ${daily_allowance:.2f}")
        
        return analysis
        
    except Exception as e:
        print(f"Error generating budget analysis: {e}")
        return analysis


def calculate_compound_interest(principal, rate, time, frequency=12):
    """
    Calculate compound interest.
    
    Args:
        principal (float): Initial amount
        rate (float): Annual interest rate (as percentage)
        time (float): Time in years
        frequency (int): Compounding frequency per year
        
    Returns:
        dict: Calculation results
    """
    try:
        # Convert percentage to decimal
        r = rate / 100
        
        # Compound interest formula: A = P(1 + r/n)^(nt)
        amount = principal * (1 + r/frequency) ** (frequency * time)
        interest_earned = amount - principal
        
        return {
            'principal': principal,
            'rate': rate,
            'time': time,
            'frequency': frequency,
            'final_amount': round(amount, 2),
            'interest_earned': round(interest_earned, 2),
            'description': f"${principal:.2f} at {rate}% for {time} years = ${amount:.2f}"
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_tip(bill_amount, tip_percentage):
    """
    Calculate tip amount and total bill.
    
    Args:
        bill_amount (float): Original bill amount
        tip_percentage (float): Tip percentage
        
    Returns:
        dict: Tip calculation results
    """
    try:
        tip_amount = bill_amount * (tip_percentage / 100)
        total_amount = bill_amount + tip_amount
        
        return {
            'bill_amount': bill_amount,
            'tip_percentage': tip_percentage,
            'tip_amount': round(tip_amount, 2),
            'total_amount': round(total_amount, 2),
            'description': f"Bill: ${bill_amount:.2f}, Tip ({tip_percentage}%): ${tip_amount:.2f}, Total: ${total_amount:.2f}"
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_split_bill(total_amount, number_of_people, tip_percentage=0):
    """
    Calculate how to split a bill among multiple people.
    
    Args:
        total_amount (float): Total bill amount
        number_of_people (int): Number of people splitting the bill
        tip_percentage (float): Tip percentage to add
        
    Returns:
        dict: Split bill calculation
    """
    try:
        if number_of_people <= 0:
            return {'error': 'Number of people must be greater than 0'}
        
        # Add tip if specified
        if tip_percentage > 0:
            tip_amount = total_amount * (tip_percentage / 100)
            total_with_tip = total_amount + tip_amount
        else:
            tip_amount = 0
            total_with_tip = total_amount
        
        per_person = total_with_tip / number_of_people
        
        return {
            'original_bill': total_amount,
            'tip_percentage': tip_percentage,
            'tip_amount': round(tip_amount, 2),
            'total_with_tip': round(total_with_tip, 2),
            'number_of_people': number_of_people,
            'per_person': round(per_person, 2),
            'description': f"${total_with_tip:.2f} split {number_of_people} ways = ${per_person:.2f} per person"
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_unit_conversion(value, from_unit, to_unit):
    """
    Perform basic unit conversions.
    
    Args:
        value (float): Value to convert
        from_unit (str): Source unit
        to_unit (str): Target unit
        
    Returns:
        dict: Conversion result
    """
    # Define conversion factors (to meters for length, to grams for weight, etc.)
    conversions = {
        # Length (to meters)
        'inch': 0.0254,
        'feet': 0.3048,
        'yard': 0.9144,
        'mile': 1609.34,
        'cm': 0.01,
        'meter': 1.0,
        'km': 1000.0,
        
        # Weight (to grams)
        'oz': 28.3495,
        'pound': 453.592,
        'gram': 1.0,
        'kg': 1000.0,
        
        # Temperature (special handling)
        'fahrenheit': 'special',
        'celsius': 'special',
        'kelvin': 'special'
    }
    
    try:
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # Special handling for temperature
        if 'fahrenheit' in [from_unit, to_unit] or 'celsius' in [from_unit, to_unit]:
            return convert_temperature(value, from_unit, to_unit)
        
        # Check if units are in the same category
        from_factor = conversions.get(from_unit)
        to_factor = conversions.get(to_unit)
        
        if from_factor is None or to_factor is None:
            return {'error': f'Unsupported unit conversion: {from_unit} to {to_unit}'}
        
        # Convert to base unit, then to target unit
        base_value = value * from_factor
        result = base_value / to_factor
        
        return {
            'original_value': value,
            'from_unit': from_unit,
            'to_unit': to_unit,
            'result': round(result, 4),
            'description': f"{value} {from_unit} = {result:.4f} {to_unit}"
        }
        
    except Exception as e:
        return {'error': str(e)}


def convert_temperature(value, from_unit, to_unit):
    """
    Convert between temperature units.
    
    Args:
        value (float): Temperature value
        from_unit (str): Source unit (fahrenheit, celsius, kelvin)
        to_unit (str): Target unit
        
    Returns:
        dict: Temperature conversion result
    """
    try:
        # Convert to Celsius first
        if from_unit == 'fahrenheit':
            celsius = (value - 32) * 5/9
        elif from_unit == 'kelvin':
            celsius = value - 273.15
        else:  # celsius
            celsius = value
        
        # Convert from Celsius to target
        if to_unit == 'fahrenheit':
            result = celsius * 9/5 + 32
        elif to_unit == 'kelvin':
            result = celsius + 273.15
        else:  # celsius
            result = celsius
        
        return {
            'original_value': value,
            'from_unit': from_unit,
            'to_unit': to_unit,
            'result': round(result, 2),
            'description': f"{value}° {from_unit.title()} = {result:.2f}° {to_unit.title()}"
        }
        
    except Exception as e:
        return {'error': str(e)}


def calculate_grade_average(grades, weights=None):
    """
    Calculate weighted or simple average of grades.
    
    Args:
        grades (list): List of grade values
        weights (list, optional): List of weights for each grade
        
    Returns:
        dict: Grade calculation results
    """
    try:
        if not grades:
            return {'error': 'No grades provided'}
        
        # Convert to floats
        grade_values = [float(g) for g in grades]
        
        if weights:
            if len(weights) != len(grades):
                return {'error': 'Number of weights must match number of grades'}
            
            weight_values = [float(w) for w in weights]
            
            # Weighted average
            weighted_sum = sum(g * w for g, w in zip(grade_values, weight_values))
            total_weight = sum(weight_values)
            
            if total_weight == 0:
                return {'error': 'Total weight cannot be zero'}
            
            average = weighted_sum / total_weight
            calculation_type = 'weighted'
        else:
            # Simple average
            average = sum(grade_values) / len(grade_values)
            calculation_type = 'simple'
        
        # Determine letter grade (assuming standard scale)
        if average >= 90:
            letter_grade = 'A'
        elif average >= 80:
            letter_grade = 'B'
        elif average >= 70:
            letter_grade = 'C'
        elif average >= 60:
            letter_grade = 'D'
        else:
            letter_grade = 'F'
        
        return {
            'grades': grade_values,
            'weights': weights,
            'calculation_type': calculation_type,
            'average': round(average, 2),
            'letter_grade': letter_grade,
            'description': f"{calculation_type.title()} average: {average:.2f} ({letter_grade})"
        }
        
    except Exception as e:
        return {'error': str(e)}


def parse_math_expression(text):
    """
    Parse natural language math expressions.
    
    Args:
        text (str): Natural language math expression
        
    Returns:
        str: Parsed mathematical expression or original text
    """
    # Replace word operations with symbols
    replacements = {
        r'\bplus\b': '+',
        r'\bminus\b': '-',
        r'\btimes\b': '*',
        r'\bmultiplied by\b': '*',
        r'\bdivided by\b': '/',
        r'\bover\b': '/',
        r'\bpercent of\b': '* 0.01 *',
        r'\bsquared\b': '**2',
        r'\bcubed\b': '**3',
        r'\bto the power of\b': '**'
    }
    
    result = text.lower()
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result)
    
    # Remove common words that don't affect calculation
    words_to_remove = ['what', 'is', 'the', 'result', 'of', 'equals', 'equal']
    for word in words_to_remove:
        result = re.sub(rf'\b{word}\b', '', result)
    
    # Clean up extra spaces
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result
