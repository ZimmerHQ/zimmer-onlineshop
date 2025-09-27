"""
Customer Resolver with Safety Features
Prevents name-only attachments and requires proper disambiguation
"""
import re
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from models import Customer, Order
from utils.business_codes import resolve_customer_reference

# Scoring threshold for automatic attachment
ATTACHMENT_THRESHOLD = 0.85

def normalize_phone(phone: str) -> str:
    """Normalize phone number - remove spaces, convert Persian digits to Latin"""
    if not phone:
        return ""
    
    # Convert Persian digits to Latin
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    latin_digits = "0123456789"
    for p, l in zip(persian_digits, latin_digits):
        phone = phone.replace(p, l)
    
    # Remove all non-digit characters
    phone = re.sub(r'[^\d]', '', phone)
    
    # Handle Iranian phone numbers
    if phone.startswith('0') and len(phone) == 11:
        return phone
    elif phone.startswith('98') and len(phone) == 13:
        return '0' + phone[2:]
    elif phone.startswith('+98') and len(phone) == 14:
        return '0' + phone[3:]
    
    return phone

def normalize_email(email: str) -> str:
    """Normalize email address"""
    if not email:
        return ""
    return email.strip().lower()

def normalize_code(code: str) -> str:
    """Normalize customer/order codes"""
    if not code:
        return ""
    return code.strip().upper()

def normalize_text(text: str) -> str:
    """Normalize Persian text - trim, normalize spaces"""
    if not text:
        return ""
    
    # Convert Persian digits to Latin
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    latin_digits = "0123456789"
    for p, l in zip(persian_digits, latin_digits):
        text = text.replace(p, l)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def mask_phone(phone: str) -> str:
    """Mask phone number for display (show last 4 digits)"""
    if not phone or len(phone) < 4:
        return "****"
    return "****" + phone[-4:]

def mask_email(email: str) -> str:
    """Mask email for display"""
    if not email or '@' not in email:
        return "****@****"
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        return "**@" + domain
    return local[:2] + "**@" + domain

def calculate_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two names (0.0 to 1.0)"""
    if not name1 or not name2:
        return 0.0
    
    name1 = normalize_text(name1).lower()
    name2 = normalize_text(name2).lower()
    
    if name1 == name2:
        return 1.0
    
    # Simple similarity based on common characters
    set1 = set(name1)
    set2 = set(name2)
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def get_customer_candidates(db: Session, query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Get customer candidates based on query with scoring"""
    query = normalize_text(query)
    candidates = []
    
    # Try exact matches first (phone, email, code)
    normalized_phone = normalize_phone(query)
    if normalized_phone:
        customer = db.query(Customer).filter(Customer.phone == normalized_phone).first()
        if customer:
            candidates.append({
                "customer": customer,
                "score": 1.0,
                "match_type": "phone_exact"
            })
    
    # Try customer code
    normalized_code = normalize_code(query)
    if normalized_code.startswith('CUS-'):
        customer = db.query(Customer).filter(Customer.customer_code == normalized_code).first()
        if customer:
            candidates.append({
                "customer": customer,
                "score": 1.0,
                "match_type": "code_exact"
            })
    
    # Try order code lookup
    if normalized_code.startswith('ORD-'):
        order = db.query(Order).filter(Order.order_code == normalized_code).first()
        if order and order.customer:
            candidates.append({
                "customer": order.customer,
                "score": 0.95,
                "match_type": "order_code"
            })
    
    # Try name-based search (for disambiguation)
    # Extract potential names from the query
    name_parts = query.split()
    if len(name_parts) >= 1:  # At least one name
        # Try different name combinations
        search_terms = []
        
        if len(name_parts) >= 2:
            # Full name: "علی رضایی"
            search_terms.append((name_parts[0], ' '.join(name_parts[1:])))
        
        # Single name: "علی" or "عرشیا"
        search_terms.append((name_parts[0], ""))
        
        for first_name, last_name in search_terms:
            # Search for customers with similar names
            if last_name:
                customers = db.query(Customer).filter(
                    or_(
                        func.lower(Customer.first_name).like(f"%{first_name.lower()}%"),
                        func.lower(Customer.last_name).like(f"%{last_name.lower()}%")
                    )
                ).limit(10).all()
            else:
                customers = db.query(Customer).filter(
                    or_(
                        func.lower(Customer.first_name).like(f"%{first_name.lower()}%"),
                        func.lower(Customer.last_name).like(f"%{first_name.lower()}%")
                    )
                ).limit(10).all()
            
            for customer in customers:
                if last_name:
                    first_sim = calculate_name_similarity(first_name, customer.first_name)
                    last_sim = calculate_name_similarity(last_name, customer.last_name)
                    avg_sim = (first_sim + last_sim) / 2
                else:
                    # For single name, check both first and last name
                    first_sim = calculate_name_similarity(first_name, customer.first_name)
                    last_sim = calculate_name_similarity(first_name, customer.last_name)
                    avg_sim = max(first_sim, last_sim)  # Take the better match
                
                if avg_sim > 0.3:  # Minimum similarity threshold
                    candidates.append({
                        "customer": customer,
                        "score": avg_sim,
                        "match_type": "name_fuzzy"
                    })
    
    # Sort by score and remove duplicates
    seen_ids = set()
    unique_candidates = []
    for candidate in sorted(candidates, key=lambda x: x["score"], reverse=True):
        if candidate["customer"].id not in seen_ids:
            seen_ids.add(candidate["customer"].id)
            unique_candidates.append(candidate)
    
    return unique_candidates[:limit]

def format_candidate_for_display(candidate: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Format candidate for safe display (no PII, no customer codes)"""
    customer = candidate["customer"]
    
    # Get last order date if available
    last_order = db.query(Order).filter(Order.customer_phone == customer.phone).order_by(Order.created_at.desc()).first()
    last_order_at = last_order.created_at.isoformat() if last_order and last_order.created_at else None
    
    return {
        "customer_id": customer.id,  # Use internal ID instead of customer code
        "masked_phone": mask_phone(customer.phone),
        "masked_email": mask_email(customer.email) if hasattr(customer, 'email') and customer.email else None,
        "city": customer.address.split(',')[0].strip() if customer.address else None,
        "last_order_at": last_order_at,
        "score": candidate["score"],
        "match_type": candidate["match_type"]
    }

def resolve_customer_safe(db: Session, query: str, verifier: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely resolve customer with disambiguation support.
    
    Args:
        db: Database session
        query: Customer query (name, phone, email, code, order_code)
        verifier: Optional verifier (postal_code, phone_last4, order_code)
    
    Returns:
        Either:
        - {"customer": customer_dict, "confidence": float} for direct attachment
        - {"needs_confirmation": True, "candidates": [...]} for disambiguation
    """
    query = normalize_text(query)
    verifier = normalize_text(verifier) if verifier else None
    
    # Get candidates
    candidates = get_customer_candidates(db, query, limit=3)
    
    if not candidates:
        return {"needs_confirmation": True, "candidates": []}
    
    # Check if we have a high-confidence match
    best_candidate = candidates[0]
    
    # Direct attachment conditions
    if best_candidate["score"] >= ATTACHMENT_THRESHOLD:
        # Additional verification if verifier provided
        if verifier:
            customer = best_candidate["customer"]
            
            # Check postal code
            if customer.postal_code and verifier == normalize_text(customer.postal_code):
                return {
                    "customer": {
                        "id": customer.id,
                        "customer_code": customer.customer_code,
                        "first_name": customer.first_name,
                        "last_name": customer.last_name,
                        "phone": customer.phone,
                        "address": customer.address,
                        "postal_code": customer.postal_code,
                        "notes": customer.notes or ""
                    },
                    "confidence": best_candidate["score"]
                }
            
            # Check phone last 4
            if customer.phone and verifier == customer.phone[-4:]:
                return {
                    "customer": {
                        "id": customer.id,
                        "customer_code": customer.customer_code,
                        "first_name": customer.first_name,
                        "last_name": customer.last_name,
                        "phone": customer.phone,
                        "address": customer.address,
                        "postal_code": customer.postal_code,
                        "notes": customer.notes or ""
                    },
                    "confidence": best_candidate["score"]
                }
            
            # Check order code
            if verifier.startswith('ORD-'):
                order = db.query(Order).filter(Order.order_code == verifier).first()
                if order and order.customer_id == customer.id:
                    return {
                        "customer": {
                            "id": customer.id,
                            "customer_code": customer.customer_code,
                            "first_name": customer.first_name,
                            "last_name": customer.last_name,
                            "phone": customer.phone,
                            "address": customer.address,
                            "postal_code": customer.postal_code,
                            "notes": customer.notes or ""
                        },
                        "confidence": best_candidate["score"]
                    }
        
        # No verifier needed for high-confidence matches
        elif best_candidate["match_type"] in ["phone_exact", "code_exact", "order_code"]:
            customer = best_candidate["customer"]
            return {
                "customer": {
                    "id": customer.id,
                    "customer_code": customer.customer_code,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "phone": customer.phone,
                    "address": customer.address,
                    "postal_code": customer.postal_code,
                    "notes": customer.notes or ""
                },
                "confidence": best_candidate["score"]
            }
    
    # Need disambiguation
    formatted_candidates = [format_candidate_for_display(c, db) for c in candidates]
    
    return {
        "needs_confirmation": True,
        "candidates": formatted_candidates
    }

def resolve_customer_by_id(db: Session, customer_id: int) -> Optional[Dict[str, Any]]:
    """Resolve customer by internal ID (for selection after disambiguation)"""
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            return {
                "id": customer.id,
                "customer_code": customer.customer_code,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone": customer.phone,
                "address": customer.address,
                "postal_code": customer.postal_code,
                "notes": customer.notes or ""
            }
        return None
    except Exception as e:
        print(f"Error resolving customer by ID: {e}")
        return None
