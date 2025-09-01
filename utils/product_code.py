from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import re
from models import Category, Product


def generate_code_for_category(db: Session, category_id: int) -> str:
    """
    Generates a unique product code for a category.
    
    Format: {prefix}{number:04d} (e.g., A0001, A0002, B0001)
    
    Args:
        db: Database session
        category_id: ID of the category
        
    Returns:
        str: Generated product code
        
    Raises:
        ValueError: If category doesn't exist or code generation fails
    """
    # Fetch category to get prefix
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise ValueError(f"Category with ID {category_id} not found")
    
    prefix = category.prefix
    
    # Find the highest existing code number for this category
    next_number = _get_next_sequence_number(db, category_id, prefix)
    
    # Generate code with retry logic for race conditions
    max_attempts = 5
    for attempt in range(max_attempts):
        code = f"{prefix}{next_number:04d}"
        
        # Check if code already exists
        existing = db.query(Product.code).filter(Product.code == code).first()
        if not existing:
            return code
        
        # Code exists, try next number
        next_number += 1
        
        # If we've tried too many times, log warning
        if attempt == max_attempts - 1:
            raise ValueError(
                f"Could not generate unique product code for category {category_id} "
                f"after {max_attempts} attempts. Last attempted: {code}"
            )
    
    # This should never be reached due to the raise above
    raise ValueError("Unexpected error in code generation")


def _get_next_sequence_number(db: Session, category_id: int, prefix: str) -> int:
    """
    Get the next sequence number for a category by parsing existing codes.
    
    Args:
        db: Database session
        category_id: ID of the category
        prefix: Category prefix
        
    Returns:
        int: Next available sequence number
    """
    # Get all existing codes for this category
    existing_codes = db.query(Product.code).filter(
        Product.category_id == category_id
    ).all()
    
    if not existing_codes:
        return 1
    
    # Parse existing codes to find the highest number
    max_number = 0
    pattern = re.compile(f"^{re.escape(prefix)}(\\d{{4}})$")
    
    for (code,) in existing_codes:
        match = pattern.match(code)
        if match:
            number = int(match.group(1))
            max_number = max(max_number, number)
    
    return max_number + 1


def validate_product_code(code: str) -> bool:
    """
    Validate if a product code is in the correct format.
    
    Args:
        code: Product code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not code:
        return False
    
    # Format: {prefix}{4-digit number}
    # Prefix: 1-2 uppercase letters
    # Number: exactly 4 digits
    pattern = re.compile(r"^[A-Z]{1,2}\d{4}$")
    return bool(pattern.match(code))


def parse_product_code(code: str) -> Optional[dict]:
    """
    Parse a product code into its components.
    
    Args:
        code: Product code to parse
        
    Returns:
        dict: Parsed components or None if invalid
        {
            'prefix': str,
            'number': int,
            'formatted_number': str
        }
    """
    if not validate_product_code(code):
        return None
    
    # Extract prefix and number
    match = re.match(r"^([A-Z]{1,2})(\d{4})$", code)
    if not match:
        return None
    
    prefix = match.group(1)
    number = int(match.group(2))
    
    return {
        'prefix': prefix,
        'number': number,
        'formatted_number': match.group(2)
    }


def get_category_code_stats(db: Session, category_id: int) -> dict:
    """
    Get statistics about product codes for a category.
    
    Args:
        db: Database session
        category_id: ID of the category
        
    Returns:
        dict: Code statistics
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return {}
    
    # Get all codes for this category
    codes = db.query(Product.code).filter(
        Product.category_id == category_id
    ).order_by(Product.code).all()
    
    if not codes:
        return {
            'category_id': category_id,
            'prefix': category.prefix,
            'total_products': 0,
            'next_code': f"{category.prefix}0001",
            'code_range': None
        }
    
    # Parse codes to get statistics
    parsed_codes = []
    for (code,) in codes:
        parsed = parse_product_code(code)
        if parsed:
            parsed_codes.append(parsed)
    
    if not parsed_codes:
        return {
            'category_id': category_id,
            'prefix': category.prefix,
            'total_products': len(codes),
            'next_code': f"{category.prefix}0001",
            'code_range': None
        }
    
    numbers = [p['number'] for p in parsed_codes]
    min_number = min(numbers)
    max_number = max(numbers)
    next_number = max_number + 1
    
    return {
        'category_id': category_id,
        'prefix': category.prefix,
        'total_products': len(codes),
        'next_code': f"{category.prefix}{next_number:04d}",
        'code_range': {
            'min': f"{category.prefix}{min_number:04d}",
            'min_number': min_number,
            'max': f"{category.prefix}{max_number:04d}",
            'max_number': max_number
        },
        'missing_codes': _find_missing_codes(numbers, category.prefix)
    }


def _find_missing_codes(numbers: list, prefix: str) -> list:
    """
    Find missing sequence numbers in a list of numbers.
    
    Args:
        db: Database session
        category_id: ID of the category
        prefix: Category prefix
        
    Returns:
        list: List of missing codes
    """
    if not numbers:
        return []
    
    min_num = min(numbers)
    max_num = max(numbers)
    
    missing = []
    for num in range(min_num, max_num + 1):
        if num not in numbers:
            missing.append(f"{prefix}{num:04d}")
    
    return missing 