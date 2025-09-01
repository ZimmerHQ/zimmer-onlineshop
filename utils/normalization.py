"""
Normalization helpers for product attributes.
Provides canonical mappings for colors, sizes, and other attributes.
"""

from typing import Optional, List, Dict
import re

# Canonical color mappings (Persian + English + abbreviations)
CANON_COLORS = {
    # Black variations
    "مشکی": "black", "سیاه": "black", "black": "black", "bk": "black",
    "اسود": "black", "کال": "black", "dark": "black",
    
    # White variations
    "سفید": "white", "white": "white", "wh": "white", "سفید": "white",
    "ابید": "white", "light": "white",
    
    # Blue variations
    "آبی": "blue", "ابی": "blue", "blue": "blue", "bl": "blue",
    "نیلی": "blue", "navy": "blue", "navy blue": "blue",
    
    # Red variations
    "قرمز": "red", "red": "red", "rd": "red", "سرخ": "red",
    "احمر": "red", "crimson": "red",
    
    # Green variations
    "سبز": "green", "green": "green", "gr": "green", "خضر": "green",
    "forest": "green", "forest green": "green",
    
    # Yellow variations
    "زرد": "yellow", "yellow": "yellow", "yl": "yellow", "اصفر": "yellow",
    "gold": "yellow", "golden": "yellow",
    
    # Brown variations
    "قهوه‌ای": "brown", "brown": "brown", "br": "brown", "کاکائویی": "brown",
    "tan": "brown", "beige": "brown",
    
    # Gray variations
    "خاکستری": "gray", "gray": "gray", "grey": "gray", "gr": "gray",
    "سرمه‌ای": "gray", "silver": "gray",
    
    # Pink variations
    "صورتی": "pink", "pink": "pink", "pk": "pink", "گلگون": "pink",
    "rose": "pink", "rose pink": "pink",
    
    # Purple variations
    "بنفش": "purple", "purple": "purple", "pr": "purple", "ارغوانی": "purple",
    "violet": "purple", "violet purple": "purple",
    
    # Orange variations
    "نارنجی": "orange", "orange": "orange", "or": "orange", "ترنجی": "orange",
    "tangerine": "orange", "coral": "orange"
}

# Canonical size mappings (Persian + English + numbers)
CANON_SIZES = {
    # Small sizes
    "اسمال": "S", "کوچک": "S", "s": "S", "small": "S", "xs": "XS",
    "خیلی کوچک": "XS", "extra small": "XS",
    
    # Medium sizes
    "مدیوم": "M", "متوسط": "M", "m": "M", "medium": "M",
    "معمولی": "M", "عادی": "M",
    
    # Large sizes
    "لارج": "L", "بزرگ": "L", "l": "L", "large": "L",
    "بزرگتر": "L", "bigger": "L",
    
    # Extra Large sizes
    "xl": "XL", "ایکس لارج": "XL", "extra large": "XL",
    "خیلی بزرگ": "XL", "very large": "XL",
    
    # XXL sizes
    "xxl": "XXL", "۲xl": "XXL", "double xl": "XXL",
    "خیلی خیلی بزرگ": "XXL", "extra extra large": "XXL",
    
    # Shoe sizes (Persian + English digits)
    "۴۰": "40", "40": "40", "forty": "40", "چهل": "40",
    "۴۱": "41", "41": "41", "forty-one": "41", "چهل و یک": "41",
    "۴۲": "42", "42": "42", "forty-two": "42", "چهل و دو": "42",
    "۴۳": "43", "43": "43", "forty-three": "43", "چهل و سه": "43",
    "۴۴": "44", "44": "44", "forty-four": "44", "چهل و چهار": "44",
    "۴۵": "45", "45": "45", "forty-five": "45", "چهل و پنج": "45",
    "۴۶": "46", "46": "46", "forty-six": "46", "چهل و شش": "46",
    "۴۷": "47", "47": "47", "forty-seven": "47", "چهل و هفت": "47",
    "۴۸": "48", "48": "48", "forty-eight": "48", "چهل و هشت": "48",
    "۴۹": "49", "49": "49", "forty-nine": "49", "چهل و نه": "49",
    
    # European sizes
    "۳۶": "36", "36": "36", "thirty-six": "36",
    "۳۷": "37", "37": "37", "thirty-seven": "37",
    "۳۸": "38", "38": "38", "thirty-eight": "38",
    "۳۹": "39", "39": "39", "thirty-nine": "39",
    
    # Generic number sizes
    "۵۰": "50", "50": "50", "fifty": "50",
    "۵۱": "51", "51": "51", "fifty-one": "51",
    "۵۲": "52", "52": "52", "fifty-two": "52"
}

def normalize_color(token: str) -> Optional[str]:
    """
    Normalize color token to canonical form.
    
    Args:
        token: Input color string
        
    Returns:
        Canonical color string or None if not recognized
    """
    if not token:
        return None
    
    t = token.strip().lower()
    return CANON_COLORS.get(t)

def normalize_size(token: str) -> Optional[str]:
    """
    Normalize size token to canonical form.
    
    Args:
        token: Input size string
        
    Returns:
        Canonical size string or None if not recognized
    """
    if not token:
        return None
    
    t = token.strip().lower()
    
    # Convert Persian digits to ASCII
    persian_to_ascii = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    
    for persian, ascii in persian_to_ascii.items():
        t = t.replace(persian, ascii)
    
    # Check canonical mappings first
    if t in CANON_SIZES:
        return CANON_SIZES[t]
    
    # If it's a pure number, return as is
    if t.isdigit():
        return t
    
    # If it's a recognized abbreviation, return canonical
    if t in CANON_SIZES:
        return CANON_SIZES[t]
    
    return None

def extract_product_code(text: str) -> Optional[str]:
    """
    Extract product code from text using regex patterns.
    
    Args:
        text: Input text to search for product codes
        
    Returns:
        Product code if found, None otherwise
    """
    if not text:
        return None
    
    # Pattern 1: A0001 style (letter + 4 digits)
    pattern1 = r'\b[A-Z]{1,3}\d{3,}\b'
    match1 = re.search(pattern1, text.upper())
    if match1:
        return match1.group()
    
    # Pattern 2: Letter + digits (more flexible)
    pattern2 = r'\b[A-Z]+\d+\b'
    match2 = re.search(pattern2, text.upper())
    if match2:
        return match2.group()
    
    return None

def clean_labels(labels: List[str]) -> List[str]:
    """
    Clean and normalize labels list.
    
    Args:
        labels: List of label strings
        
    Returns:
        Cleaned list with duplicates removed and normalized
    """
    if not labels:
        return []
    
    cleaned = []
    seen = set()
    
    for label in labels:
        if label:
            clean_label = label.strip().lower()
            if clean_label and clean_label not in seen:
                cleaned.append(clean_label)
                seen.add(clean_label)
    
    return cleaned

def clean_attributes(attributes: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Clean and normalize attributes dictionary.
    
    Args:
        attributes: Dictionary of attribute keys to value lists
        
    Returns:
        Cleaned dictionary with normalized values
    """
    if not attributes:
        return {}
    
    cleaned = {}
    
    for key, values in attributes.items():
        if key and values:
            clean_key = key.strip().lower()
            clean_values = []
            seen = set()
            
            for value in values:
                if value:
                    clean_value = value.strip().lower()
                    if clean_value and clean_value not in seen:
                        clean_values.append(clean_value)
                        seen.add(clean_value)
            
            if clean_values:
                cleaned[clean_key] = clean_values
    
    return cleaned

def tokenize_search_query(query: str) -> List[str]:
    """
    Tokenize search query into meaningful tokens.
    
    Args:
        query: Search query string
        
    Returns:
        List of normalized tokens
    """
    if not query:
        return []
    
    # Split by common separators and clean
    tokens = re.split(r'[\s,،]+', query)
    
    # Clean and normalize tokens
    cleaned = []
    for token in tokens:
        if token:
            clean_token = token.strip().lower()
            if clean_token:
                cleaned.append(clean_token)
    
    return cleaned

def extract_attributes_from_query(query: str) -> Dict[str, List[str]]:
    """
    Extract potential attributes from search query.
    
    Args:
        query: Search query string
        
    Returns:
        Dictionary of extracted attributes
    """
    tokens = tokenize_search_query(query)
    attributes = {}
    
    for token in tokens:
        # Check if token is a color
        color = normalize_color(token)
        if color:
            if "color" not in attributes:
                attributes["color"] = []
            if color not in attributes["color"]:
                attributes["color"].append(color)
        
        # Check if token is a size
        size = normalize_size(token)
        if size:
            if "size" not in attributes:
                attributes["size"] = []
            if size not in attributes["size"]:
                attributes["size"].append(size)
    
    return attributes 