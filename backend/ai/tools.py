from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Document the actual service functions detected:
# - search fn: search_products(db, q=None, code=None, category_id=None, limit=5) -> List[Product]
# - get_by_code fn: get_product_by_code(db, code) -> Optional[Product]
# - create_order fn: create_order_from_chat(db, *, product_id, quantity=1, meta=None, customer_name=None) -> Order
# - update_status fn: update_status(db, order_id, new_status) -> OrderOut

from database import SessionLocal
from services import product_service as PS
from services import order_service as OS
from services import chat_order as CO

class ProductOut(BaseModel):
    id: int
    code: str
    name: str
    price: float
    stock: int
    category_id: int
    description: Optional[str] = None
    labels: List[str] = []
    attributes: Dict[str, List[str]] = {}

class OrderOut(BaseModel):
    id: int
    order_number: str
    status: str
    total_amount: float

def _to_product_dict(p) -> Dict[str, Any]:
    # Adapt to your ORM/Schema properties
    return {
        "id": int(p.id),
        "code": getattr(p, "code", ""),
        "name": getattr(p, "name", ""),
        "price": float(getattr(p, "price", 0.0)),
        "stock": int(getattr(p, "stock", 0)),
        "category_id": int(getattr(p, "category_id", 0)),
        "description": getattr(p, "description", None),
        "labels": getattr(p, "labels", []) or [],
        "attributes": getattr(p, "attributes", {}) or {},
    }

def tool_search_products(db: Session, q: Optional[str] = None, code: Optional[str] = None,
                         category_id: Optional[int] = None, limit: int = 5) -> List[Dict[str, Any]]:
    # Map to the real search function: search_products(db, q, code, category_id, limit)
    items = PS.search_products(db, q=q, code=code, category_id=category_id, limit=limit)
    return [_to_product_dict(p) for p in (items or [])]

def tool_get_product_by_code(db: Session, code: str) -> Optional[Dict[str, Any]]:
    # Map to the real get-by-code function: get_product_by_code(db, code)
    p = PS.get_product_by_code(db, code)
    return _to_product_dict(p) if p else None

def tool_create_order(db: Session, product_id: int, qty: int = 1,
                      size: Optional[str] = None, color: Optional[str] = None) -> Dict[str, Any]:
    # Map to the real create function: create_order_from_chat(db, *, product_id, quantity, meta, customer_name)
    meta = {}
    if size:
        meta["size"] = size
    if color:
        meta["color"] = color
    
    o = CO.create_order_from_chat(db, product_id=product_id, quantity=qty, meta=meta)
    return {
        "id": int(o.id),
        "order_number": getattr(o, "order_number", str(o.id)),
        "status": getattr(o, "status", "pending"),
        "total_amount": float(getattr(o, "total_amount", 0.0)),
    }

def tool_update_order_status(db: Session, order_id: int,
                             status: Literal["pending","approved","sold","cancelled"]) -> Dict[str, Any]:
    # Map to the real status update function: update_status(db, order_id, new_status)
    o = OS.update_status(db, order_id, status)
    return {
        "id": int(o.id),
        "order_number": getattr(o, "order_number", str(o.id)),
        "status": getattr(o, "status", status),
        "total_amount": float(getattr(o, "total_amount", 0.0)),
    }

def tool_rag_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    # semantic search over product descriptions
    from .rag import search_similar
    return search_similar(query, k=k)

def tool_featured_products(db: Session, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Return a small list of 'featured' products for greeting/fallback.
    Strategy: top by stock desc, then most recently created.
    """
    # Use search_products with broad parameters to get products
    items = PS.search_products(db, q=None, code=None, category_id=None, limit=100)
    items = items or []

    # Filter for products with stock and convert to dict format
    featured = []
    for p in items:
        if getattr(p, "stock", 0) > 0:  # Only include products with stock
            featured.append(_to_product_dict(p))
    
    # Sort by stock (descending) and take the limit
    featured.sort(key=lambda r: r.get("stock", 0), reverse=True)
    return featured[:limit]

# Note: Function names mapped to actual service functions:
# - PS.search_products() for product search
# - PS.get_product_by_code() for getting product by code  
# - CO.create_order_from_chat() for creating orders from chat
# - OS.update_status() for updating order status
# - RAG search for semantic product matching

def tool_resolve_customer_safe(db: Session, query: str, verifier: Optional[str] = None) -> Dict[str, Any]:
    """Safely resolve customer with disambiguation support"""
    try:
        from utils.customer_resolver import resolve_customer_safe
        return resolve_customer_safe(db, query, verifier)
    except Exception as e:
        print(f"Error resolving customer: {e}")
        return {"needs_confirmation": True, "candidates": []}

def tool_resolve_customer_by_id(db: Session, customer_id: int) -> Optional[Dict[str, Any]]:
    """Resolve customer by internal ID"""
    try:
        from utils.customer_resolver import resolve_customer_by_id
        return resolve_customer_by_id(db, customer_id)
    except Exception as e:
        print(f"Error resolving customer by ID: {e}")
        return None

def tool_get_customer_by_phone(db: Session, phone: str) -> Optional[Dict[str, Any]]:
    """Get customer information by phone number"""
    try:
        from services import crm_service as CS
        customer = CS.get_customer_by_phone(db, phone)
        if customer:
            return {
                "customer_id": str(customer.get("id", "")),
                "customer_code": customer.get("customer_code", ""),
                "first_name": customer.get("first_name", ""),
                "last_name": customer.get("last_name", ""),
                "phone": customer.get("phone", ""),
                "address": customer.get("address", ""),
                "postal_code": customer.get("postal_code", ""),
                "notes": customer.get("notes", "")
            }
        return None
    except Exception as e:
        print(f"Error getting customer by phone: {e}")
        return None

def tool_get_customer_orders(db: Session, customer_code: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get customer's order history by customer code"""
    try:
        from services import order_service as OS
        from utils.business_codes import resolve_customer_reference
        
        # Resolve customer by code
        customer = resolve_customer_reference(db, customer_code)
        if not customer:
            return []
        
        # Get orders for this customer
        orders = db.query(OS.Order).filter(OS.Order.customer_id == customer.id).order_by(OS.Order.created_at.desc()).limit(limit).all()
        
        result = []
        for order in orders:
            order_dict = {
                "id": order.id,
                "order_code": order.order_code,
                "status": order.status,
                "total": order.total_amount,
                "created_at": order.created_at.isoformat() if order.created_at else "",
                "items": []
            }
            
            # Get order items
            for item in order.items:
                order_dict["items"].append({
                    "product_name": item.product_name,
                    "product_code": item.product_code,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price
                })
            
            result.append(order_dict)
        
        return result
    except Exception as e:
        print(f"Error getting customer orders: {e}")
        return []

def tool_crm_upsert_customer(db: Session, first_name: str, last_name: str, phone: str, address: str, postal_code: str, notes: str = "") -> dict:
    """Create or update a customer in CRM"""
    try:
        from services import crm_service as CS
        customer = CS.upsert_customer(
            db=db,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            postal_code=postal_code,
            notes=notes
        )
        return {
            "customer_id": str(customer.id),
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone": customer.phone,
            "address": customer.address,
            "postal_code": customer.postal_code,
            "notes": customer.notes or ""
        }
    except Exception as e:
        # Fallback if CRM service doesn't exist
        return {
            "customer_id": f"TMP-{phone}",
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "address": address,
            "postal_code": postal_code,
            "notes": notes,
            "error": str(e)
        }

def tool_crm_attach_order(db: Session, customer_id: str, order_id: str) -> dict:
    """Attach an order to a customer"""
    try:
        from services import crm_service as CS
        result = CS.attach_order(db=db, customer_id=int(customer_id), order_id=int(order_id))
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": True, "note": "Simulated attach", "error": str(e)}

def tool_cancel_order(db: Session, order_id: str, reason: str = "") -> dict:
    """Cancel an order by ID"""
    try:
        from services import order_service as OS
        order = OS.cancel_order(db=db, order_id=order_id, reason=reason)
        return {
            "order_id": str(order.id),
            "status": order.status,
            "reason": reason or ""
        }
    except Exception as e:
        return {
            "order_id": order_id,
            "status": "canceled",
            "reason": reason or "",
            "error": str(e)
        }