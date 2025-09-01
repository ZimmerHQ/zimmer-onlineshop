from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from models import Category


def assign_next_category_prefix(db: Session) -> str:
    """
    Assigns the next available category prefix.
    
    Prefix sequence: A, B, C, ..., Z, AA, AB, AC, ..., AZ, BA, BB, ..., ZZ
    Maximum supported: ZZ (676 categories)
    
    Args:
        db: Database session
        
    Returns:
        str: Next available prefix (e.g., 'A', 'B', 'AA', etc.)
        
    Raises:
        ValueError: If all prefixes are exhausted (after ZZ)
    """
    # Count existing categories
    count = db.query(func.count(Category.id)).scalar()
    
    if count == 0:
        return 'A'
    
    # Calculate next prefix
    if count < 26:
        # Single letters: A-Z (0-25)
        return chr(65 + count)  # 65 = 'A'
    elif count < 26 + 26*26:
        # Double letters: AA-ZZ (26-701)
        remaining = count - 26
        first_char = chr(65 + (remaining // 26))
        second_char = chr(65 + (remaining % 26))
        return f"{first_char}{second_char}"
    else:
        # Exhausted all reasonable prefixes (after ZZ)
        raise ValueError(
            f"All category prefixes have been exhausted. "
            f"Maximum supported: 676 categories (A-Z, AA-ZZ). "
            f"Current count: {count}"
        )


def get_prefix_info(db: Session) -> dict:
    """
    Get information about current prefix usage.
    
    Args:
        db: Database session
        
    Returns:
        dict: Information about prefix usage
    """
    # Get all existing prefixes
    prefixes = db.query(Category.prefix).order_by(Category.prefix).all()
    prefix_list = [p[0] for p in prefixes]
    
    # Count by length
    single_letter = len([p for p in prefix_list if len(p) == 1])
    double_letter = len([p for p in prefix_list if len(p) == 2])
    
    # Find next available prefix
    try:
        next_prefix = assign_next_category_prefix(db)
    except ValueError:
        next_prefix = "EXHAUSTED"
    
    return {
        "total_categories": len(prefix_list),
        "single_letter_prefixes": single_letter,
        "double_letter_prefixes": double_letter,
        "current_prefixes": prefix_list,
        "next_available_prefix": next_prefix,
        "max_supported": 26 + 26*26,  # A-Z + AA-ZZ
        "remaining_capacity": max(0, (26 + 26*26) - len(prefix_list))
    }


def validate_prefix(prefix: str) -> bool:
    """
    Validate if a prefix is in the correct format.
    
    Args:
        prefix: Prefix to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not prefix:
        return False
    
    if len(prefix) > 2:
        return False
    
    # Check if all characters are uppercase letters
    return all(65 <= ord(c) <= 90 for c in prefix)  # A-Z = 65-90 