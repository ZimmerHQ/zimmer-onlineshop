"""
Agent Tools - Clean wrapper functions for the sales agent
"""
import hashlib
import hmac
import json
import os
from langchain_core.tools import tool

PRICE_UNIT = "تومان"

# Order confirmation secret
_CONFIRM_SECRET = os.getenv("ORDER_CONFIRM_SECRET", "dev-secret")

def _sign(payload: dict) -> str:
    """Sign a payload with HMAC-SHA256"""
    msg = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hmac.new(_CONFIRM_SECRET.encode("utf-8"), msg, hashlib.sha256).hexdigest()

def _verify(payload: dict, token: str) -> bool:
    """Verify a payload against its token"""
    return hmac.compare_digest(_sign(payload), token)

def _required_missing(proposal: dict) -> list[str]:
    """Check what required fields are missing from a proposal"""
    missing = []
    # qty required and must be >=1
    if "qty" not in proposal or str(proposal["qty"]).strip() == "" or int(proposal["qty"]) < 1:
        missing.append("qty")
    # customer required
    cust = proposal.get("customer") if isinstance(proposal.get("customer"), dict) else {}
    for key in ("first_name","last_name","phone","address","postal_code"):
        if not cust.get(key):
            missing.append(f"customer.{key}")
    return missing

def _fmt_price(v):
    try:
        n = int(float(v))
        s = f"{n:,}".replace(",", "٬")
    except Exception:
        s = str(v)
    return f"{s} {PRICE_UNIT}"

@tool
def list_products(limit: int = 3) -> list:
    """List a few popular products for browsing or greeting. Use when the user is undecided or says hello."""
    try:
        from .tools import tool_featured_products
        from .agent import get_db_session
        db = get_db_session()
        if not db:
            return []
        items = tool_featured_products(db=db, limit=limit) or []
        for p in items:
            p["price_text"] = _fmt_price(p.get("price", 0))
        return items
    except Exception as e:
        return []

@tool
def search_products(q: str, limit: int = 6) -> list:
    """Search products by user text (category/keywords). Use for all product inquiries without a specific code."""
    try:
        from .tools import tool_search_products
        from .agent import get_db_session
        db = get_db_session()
        if not db:
            return []
        rows = tool_search_products(db=db, q=q, limit=limit) or []
        for p in rows:
            p["price_text"] = _fmt_price(p.get("price", 0))
        return rows
    except Exception as e:
        return []

@tool
def get_product_by_code(code: str) -> dict:
    """Fetch a product by exact code like A0001. Include attributes_spec if available so the agent knows required attributes."""
    try:
        from .tools import tool_get_product_by_code
        from .agent import get_db_session
        db = get_db_session()
        if not db:
            return {}
        p = tool_get_product_by_code(db=db, code=code.upper()) or {}
        if p:
            p["price_text"] = _fmt_price(p.get("price", 0))
            # Ensure attributes_spec exists; if your DB lacks it, provide an empty list (then no attributes are required)
            p.setdefault("attributes_spec", p.get("attributes_spec") or [])
        return p
    except Exception as e:
        return {}

@tool
def similar_products(code: str, limit: int = 3) -> list:
    """Recommend similar/alternative items to a product code. Use if item is out of stock or alternatives are requested."""
    try:
        from .tools import tool_search_products
        from .agent import get_db_session
        db = get_db_session()
        if not db:
            return []
        # Use direct search instead of RAG for speed
        rows = tool_search_products(db=db, q=code.upper(), limit=limit) or []
        for p in rows:
            p["price_text"] = _fmt_price(p.get("price", 0))
        return rows
    except Exception as e:
        return []

@tool
def crm_upsert_customer(first_name: str, last_name: str, phone: str, address: str, postal_code: str, notes: str = "") -> dict:
    """Create or update a customer in CRM using exact fields. Use when customer details are provided or updated."""
    try:
        from .agent import get_db_session
        from services import crm_service
        
        db = get_db_session()
        if not db:
            return {"error": "no_db_session"}
            
        c = crm_service.upsert_customer(
            db,
            first_name=first_name, last_name=last_name,
            phone=phone, address=address, postal_code=postal_code, notes=notes
        )
        return {"customer_id": c.id, "customer_code": c.customer_code, "first_name": c.first_name, "last_name": c.last_name, "phone": c.phone}
    except Exception as e:
        return {"error": f"crm_upsert_failed: {str(e)}"}

@tool
def crm_attach_order(customer_id: str, order_id: str) -> dict:
    """Attach an existing order to a given customer. Use after order creation when a customer exists."""
    try:
        from .agent import get_db_session
        from services import crm_service
        
        db = get_db_session()
        if not db:
            return {"error": "no_db_session"}
            
        crm_service.attach_order(db, customer_id=int(customer_id), order_id=int(order_id))
        return {"ok": True}
    except Exception as e:
        return {"error": f"crm_attach_failed: {str(e)}"}

def _load_product_spec(code: str) -> list:
    """Return attributes_spec for product code. Empty list if none."""
    from .tools import tool_get_product_by_code
    from .agent import get_db_session
    db = get_db_session()
    p = tool_get_product_by_code(db=db, code=code.upper()) or {}
    spec = p.get("attributes_spec") or []
    # ensure normalized shape
    norm = []
    for s in spec:
        norm.append({
            "key": s.get("key"),
            "title": s.get("title") or s.get("key"),
            "required": bool(s.get("required")),
            "type": (s.get("type") or "string").lower(),   # string|enum|number|boolean|measure
            "values": s.get("values") or [],
            "unit": s.get("unit"),
            "min": s.get("min"),
            "max": s.get("max"),
        })
    return norm

def _validate_attributes(spec: list, attrs: dict) -> tuple[list, list]:
    """Return (missing_keys, invalid_pairs) based on spec."""
    missing = []
    invalid = []
    attrs = attrs or {}
    for s in spec:
        key = s["key"]
        if s["required"] and key not in attrs:
            missing.append(f"attributes.{key}")
            continue
        if key in attrs:
            val = str(attrs[key]).strip()
            t = s["type"]
            if t == "enum" and s["values"]:
                if val not in s["values"]:
                    invalid.append(f"attributes.{key}: expected one of {s['values']}, got {val}")
            elif t == "number":
                try:
                    num = float(val)
                    if s.get("min") is not None and num < float(s["min"]):
                        invalid.append(f"attributes.{key}: min {s['min']}, got {val}")
                    if s.get("max") is not None and num > float(s["max"]):
                        invalid.append(f"attributes.{key}: max {s['max']}, got {val}")
                except:
                    invalid.append(f"attributes.{key}: must be a number, got {val}")
            # boolean/measure/string can pass (optional: add stricter checks)
    return missing, invalid

@tool
def propose_order(code: str, qty: int | None = None, attributes: dict | None = None, customer: dict | None = None) -> dict:
    """Validate order inputs against the product's attribute spec. 
    Returns {"confirmation_token","proposal"} when ready; otherwise {"error":"missing_fields","missing":[...]} or {"error":"invalid_fields","details":[...]}."""
    code = (code or "").upper().strip()
    q = int(qty) if qty not in (None, "",) else 0
    attrs = attributes if isinstance(attributes, dict) else {}
    cust = customer if isinstance(customer, dict) else {}

    # qty required
    missing = []
    if q < 1:
        missing.append("qty")

    # customer required fields
    for k in ("first_name","last_name","phone","address","postal_code"):
        if not cust.get(k):
            missing.append(f"customer.{k}")

    # product attribute spec validation
    spec = _load_product_spec(code)
    req_missing, invalid = _validate_attributes(spec, attrs)
    missing.extend(req_missing)

    if missing:
        return {"error": "missing_fields", "missing": missing, "proposal": {"code": code, "qty": q, "attributes": attrs, "customer": cust}}
    if invalid:
        return {"error": "invalid_fields", "details": invalid, "proposal": {"code": code, "qty": q, "attributes": attrs, "customer": cust}}

    token = _sign({"code": code, "qty": q, "attributes": attrs, "customer": cust})
    return {"confirmation_token": token, "proposal": {"code": code, "qty": q, "attributes": attrs, "customer": cust}}

@tool
def place_order(confirmation_token: str, proposal: dict) -> dict:
    """Place the order ONLY if the token matches the proposal. Returns {order_id, order_code, status}."""
    if not isinstance(proposal, dict) or not confirmation_token:
        return {"error": "invalid_request"}
    if not _verify(proposal, confirmation_token):
        return {"error": "invalid_confirmation_token"}

    try:
        from .agent import get_db_session
        from services.order_service import create_order
        from services import crm_service

        db = get_db_session()
        if not db:
            return {"error": "no_db_session"}

        cust = proposal.get("customer") if isinstance(proposal.get("customer"), dict) else None

        order = create_order(
            db=db,
            code=proposal.get("code",""),
            qty=int(proposal.get("qty",1)),
            attributes=proposal.get("attributes") or {},
            customer_snapshot=cust or None
        )
        order_id = order.id
        order_code = getattr(order, "order_code", str(order_id))

        # Optional: CRM upsert + attach
        if cust and all(cust.get(k) for k in ("first_name","last_name","phone","address","postal_code")):
            c = crm_service.upsert_customer(
                db,
                first_name=cust["first_name"], last_name=cust["last_name"],
                phone=cust["phone"], address=cust["address"],
                postal_code=cust["postal_code"], notes=cust.get("notes",""),
            )
            crm_service.attach_order(db, customer_id=c.id, order_id=order_id)

        return {"order_id": str(order_id), "order_code": order_code, "status": "created"}
    except Exception as e:
        error_msg = str(e)
        # Handle specific error types with better messages
        if "Insufficient stock" in error_msg:
            return {"error": f"insufficient_stock: {error_msg}"}
        elif "not found" in error_msg:
            return {"error": f"product_not_found: {error_msg}"}
        else:
            return {"error": f"place_order_failed: {error_msg}"}

@tool
def cancel_order(order_ref: str, reason: str = "") -> dict:
    """Cancel an existing order by order_id or order_code. Use when the user requests cancellation."""
    try:
        from .agent import get_db_session
        from services import order_service
        from utils.business_codes import resolve_order_reference

        db = get_db_session()
        if not db:
            return {"error": "no_db_session"}
        
        # Resolve order by either ID or code
        order = resolve_order_reference(db, order_ref)
        if not order:
            return {"error": f"order_not_found: {order_ref}"}
            
        res = order_service.cancel_order(db, order_id=order.id, reason=reason or "")
        return {"order_id": str(order.id), "order_code": order.order_code, "status": res.get("status","canceled")}
    except Exception as e:
        return {"error": f"cancel_failed: {str(e)}"}

# ==== CUSTOMER PARSER TOOL ====
import re

def _normalize_fa(s: str) -> str:
    if not s: return ""
    s = s.replace("\u200c","")              # ZWNJ
    s = s.replace("؟","?").replace("ي","ی").replace("ك","ک")
    s = re.sub(r"\s+", " ", s).strip()
    # Persian digits → Latin
    s = s.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹","0123456789"))
    return s

def _slice_numbered_fields(text: str) -> dict:
    """
    Supports '1. X 2. Y 3. Z 4. ... 5. ... [6. ...]'
    Maps: 1→first_name, 2→last_name, 3→phone, 4→address, 5→postal_code, 6→notes
    """
    t = _normalize_fa(text)
    out = {}
    marks = list(re.finditer(r'(?P<i>[1-6])\s*[\.\:]\s*', t))
    if not marks:
        return {}
    for idx, m in enumerate(marks):
        i = int(m.group("i"))
        start = m.end()
        end = marks[idx+1].start() if idx+1 < len(marks) else len(t)
        val = t[start:end].strip(" ,;،")
        if not val: 
            continue
        if   i == 1: out["first_name"]  = val
        elif i == 2: out["last_name"]   = val
        elif i == 3: out["phone"]       = val
        elif i == 4: out["address"]     = val
        elif i == 5: out["postal_code"] = val
        elif i == 6: out["notes"]       = val
    return out

def _grab(pat, text):
    m = re.search(pat, text, flags=re.I)
    return m.group(1).strip() if m else ""

def _parse_labeled_fields(text: str) -> dict:
    """Handles: نام: …، نام خانوادگی/فامیلی: …، شماره/موبایل: …، آدرس: …، کد پستی/کدپستی: …، یادداشت/توضیحات: …"""
    t = _normalize_fa(text)
    out = {}
    out["first_name"]  = _grab(r"(?:نام|اسم)\s*[:\-]\s*([^,،\n]+)", t) or ""
    out["last_name"]   = _grab(r"(?:نام خانوادگی|فامیلی)\s*[:\-]\s*([^,،\n]+)", t) or ""
    out["phone"]       = _grab(r"(?:شماره(?:\s*تلفن)?|موبایل)\s*[:\-]\s*([+0-9]+)", t) or ""
    out["address"]     = _grab(r"(?:آدرس)\s*[:\-]\s*([^,،\n]+)", t) or ""
    out["postal_code"] = _grab(r"(?:کد\s*پستی|کدپستی)\s*[:\-]\s*([0-9]+)", t) or ""
    out["notes"]       = _grab(r"(?:یادداشت|توضیحات)\s*[:\-]\s*([^,،\n]+)", t) or ""
    # prune empties
    return {k:v for k,v in out.items() if v}

def _parse_simple_commas(text: str) -> dict:
    """
    Fallback: 'عرشیا, باغی, 0904..., تهران تهران, 7787..., [یادداشت...]'
    """
    t = _normalize_fa(text)
    parts = [p.strip() for p in re.split(r"[,،]", t) if p.strip()]
    out = {}
    if len(parts) >= 5:
        out["first_name"]  = parts[0]
        out["last_name"]   = parts[1]
        out["phone"]       = parts[2]
        out["address"]     = parts[3]
        out["postal_code"] = parts[4]
        if len(parts) >= 6:
            out["notes"] = parts[5]
    return out

@tool
def parse_customer_details(text: str) -> dict:
    """
    Parse Persian one-line customer info into:
      {first_name, last_name, phone, address, postal_code, notes?}
    Use this when the message includes several fields in one line (numbered like '1. ... 2. ...' or labeled like 'نام: ...').
    Robust to Persian digits and punctuation. Returns only the keys it can confidently extract.
    """
    t = _normalize_fa(text)
    # 1) Numbered pattern
    d = _slice_numbered_fields(t)
    # 2) Labeled pattern (fills any gaps)
    if True:
        lab = _parse_labeled_fields(t)
        for k, v in lab.items():
            d.setdefault(k, v)
    # 3) Comma-separated fallback (fills gaps)
    if True:
        cm = _parse_simple_commas(t)
        for k, v in cm.items():
            d.setdefault(k, v)
    # final cleanup for phone/postal_code: keep digits + plus
    if "phone" in d:
        d["phone"] = re.sub(r"[^\d+]", "", d["phone"])
    if "postal_code" in d:
        d["postal_code"] = re.sub(r"\D", "", d["postal_code"])
    return d

# ==== QTY AND ATTRIBUTES PARSER ====
def _norm(s: str) -> str:
    if not s: return ""
    s = s.replace("\u200c","").replace("؟","?").replace("ي","ی").replace("ك","ک")
    s = re.sub(r"\s+"," ", s).strip()
    return s.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹","0123456789"))

_QTY_PATTERNS = [
    r"(?:تعداد|qty|count)\s*[:\-]\s*(\d+)",
    r"(\d+)\s*(?:عدد|تا)\b",
    r"\bqty\s*=\s*(\d+)"
]

# generic key:value pairs like 'رنگ: مشکی' or 'capacity: 256GB'
_KV_PAT = r"([A-Za-z\u0600-\u06FF][A-Za-z0-9_\-\u0600-\u06FF ]{0,24})\s*[:=]\s*([^,،\n]+?)(?=\s*[,،]|\s*$)"

@tool
def parse_qty_and_attrs(text: str) -> dict:
    """Parse qty and generic attributes from a single Persian line. Returns {"qty": int?, "attributes":{}}.
    Attributes are returned as a raw dict (unvalidated). Keys/values kept as seen (normalized whitespace & digits)."""
    t = _norm(text)
    qty = None
    for pat in _QTY_PATTERNS:
        m = re.search(pat, t, flags=re.I)
        if m:
            try:
                qty = int(m.group(1))
                break
            except:
                pass
    
    # Extract attributes using a simpler approach
    attrs = {}
    
    # Split by common separators and look for key:value pairs
    parts = re.split(r'[,،]', t)
    
    for part in parts:
        part = part.strip()
        # Look for key:value pattern in each part
        if ':' in part or '=' in part:
            # Try to find the last occurrence of : or = to split
            for sep in [':', '=']:
                if sep in part:
                    # Find the last occurrence
                    last_sep = part.rfind(sep)
                    if last_sep > 0:
                        key = part[:last_sep].strip()
                        value = part[last_sep+1:].strip()
                        
                        # Clean up key and value
                        key = _norm(key).strip()
                        value = _norm(value).strip(" ,؛،")
                        
                        # Only accept reasonable keys (not product codes, not too long)
                        if (key and value and 
                            not re.match(r'^[A-Z0-9]+$', key) and 
                            len(key) < 20 and 
                            len(value) < 50):
                            attrs[key] = value
                    break
    
    return {"qty": qty, "attributes": attrs}

@tool
def resolve_customer(query: str, verifier: str = None) -> dict:
    """Resolve customer by code/phone/email/order_code or name + (postal|last4).
    Returns either {customer, confidence} or {needs_confirmation, candidates:[{customer_id, masked_phone, masked_email, city, last_order_at}]}.
    Never returns raw PII. Never attaches by name alone - always requires another identifier or disambiguation."""
    try:
        from .tools import tool_resolve_customer_safe
        from .agent import get_db_session
        
        db = get_db_session()
        result = tool_resolve_customer_safe(db, query, verifier)
        
        if result.get("needs_confirmation"):
            candidates = result.get("candidates", [])
            if candidates:
                return {
                    "success": True,
                    "needs_confirmation": True,
                    "candidates": candidates,
                    "message": f"چند مشتری با این نام یافت شد. لطفاً شماره مشتری یا کد پستی یا ۴ رقم آخر شماره تلفن خود را وارد کنید."
                }
            else:
                return {
                    "success": False,
                    "message": "مشتری با این مشخصات یافت نشد."
                }
        else:
            customer = result.get("customer")
            confidence = result.get("confidence", 0.0)
            return {
                "success": True,
                "customer": customer,
                "confidence": confidence,
                "message": f"مشتری شناسایی شد: {customer.get('first_name')} {customer.get('last_name')}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "خطا در شناسایی مشتری"
        }

@tool
def select_customer_by_id(customer_id: int) -> dict:
    """Select a customer by their internal ID after disambiguation.
    
    Args:
        customer_id: Internal customer ID (e.g., 1, 2, 3)
    
    Returns:
        dict with customer information
    """
    try:
        from .tools import tool_resolve_customer_by_id
        from .agent import get_db_session
        
        db = get_db_session()
        customer = tool_resolve_customer_by_id(db, customer_id)
        
        if customer:
            return {
                "success": True,
                "customer": customer,
                "message": f"مشتری انتخاب شد: {customer.get('first_name')} {customer.get('last_name')}"
            }
        else:
            return {
                "success": False,
                "message": "مشتری با این شماره یافت نشد."
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "خطا در انتخاب مشتری"
        }

@tool
def get_current_customer() -> dict:
    """Get the currently resolved customer from session memory for order creation.
    
    Returns:
        dict with customer information if available, or message to resolve customer first
    """
    try:
        from .agent import get_db_session
        db = get_db_session()
        if not db:
            return {"error": "no_db_session"}
        
        # Get the current customer from session state
        # This is a simplified version - in practice, you'd get this from the session state
        # For now, we'll return a message indicating the customer should be resolved first
        return {"message": "No customer currently resolved. Please use resolve_customer first."}
    except Exception as e:
        return {"error": f"Failed to get current customer: {str(e)}"}

@tool
def get_customer_by_phone(phone: str) -> dict:
    """Get customer information by phone number. Use this to recognize returning customers.
    
    Args:
        phone: Customer's phone number (e.g., "09123456789")
    
    Returns:
        dict with customer information including customer_code, name, and order history
    """
    try:
        from .tools import tool_get_customer_by_phone
        from .agent import get_db_session
        
        db = get_db_session()
        result = tool_get_customer_by_phone(db, phone)
        
        if result:
            return {
                "success": True,
                "customer": result,
                "message": f"سلام {result.get('first_name', '')} {result.get('last_name', '')}! خوش آمدید. کد مشتری شما: {result.get('customer_code', '')}"
            }
        else:
            return {
                "success": False,
                "message": "مشتری با این شماره تلفن یافت نشد. آیا می‌خواهید ثبت نام کنید؟"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "خطا در جستجوی مشتری"
        }

@tool
def get_customer_order_history(customer_code: str, limit: int = 5) -> dict:
    """Get customer's order history by customer code.
    
    Args:
        customer_code: Customer's business code (e.g., "CUS-2025-000001")
        limit: Maximum number of orders to return (default: 5)
    
    Returns:
        dict with customer's recent orders
    """
    try:
        from .tools import tool_get_customer_orders
        from .agent import get_db_session
        
        db = get_db_session()
        orders = tool_get_customer_orders(db, customer_code, limit)
        
        if orders:
            order_list = []
            for order in orders:
                order_list.append({
                    "order_code": order.get("order_code"),
                    "status": order.get("status"),
                    "total": order.get("total"),
                    "created_at": order.get("created_at"),
                    "items": [{"product_name": item.get("product_name"), "quantity": item.get("quantity")} for item in order.get("items", [])]
                })
            
            return {
                "success": True,
                "orders": order_list,
                "message": f"تاریخچه سفارشات شما ({len(order_list)} سفارش اخیر):"
            }
        else:
            return {
                "success": False,
                "message": "هیچ سفارشی یافت نشد."
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "خطا در دریافت تاریخچه سفارشات"
        }

@tool
def create_support_request(customer_name: str, customer_phone: str, message: str) -> dict:
    """Create a human support request when the AI cannot help the customer.
    
    Args:
        customer_name: Full name of the customer
        customer_phone: Phone number of the customer
        message: The customer's support message/issue
    
    Returns:
        dict with success status and support request details
    """
    try:
        import requests
        import os
        
        # Get API base URL from environment
        api_base = os.getenv("API_BASE_URL", "http://localhost:8000")
        
        # Create support request
        support_data = {
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "message": message
        }
        
        response = requests.post(
            f"{api_base}/api/support/requests",
            json=support_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            support_request = response.json()
            return {
                "success": True,
                "support_request_id": support_request["id"],
                "message": f"درخواست پشتیبانی شما با شماره {support_request['id']} ثبت شد. تیم پشتیبانی ما در اسرع وقت با شما تماس خواهند گرفت."
            }
        else:
            return {
                "success": False,
                "message": "متأسفانه در ثبت درخواست پشتیبانی مشکلی پیش آمد. لطفاً دوباره تلاش کنید."
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"خطا در ثبت درخواست پشتیبانی: {str(e)}"
        }

# ==== VARIANT TOOLS ====

@tool
def list_variants(product_code: str) -> dict:
    """List all variants for a product.
    
    Args:
        product_code: Product code (e.g., "A0001")
    
    Returns:
        dict with list of variants and their details
    """
    try:
        from .agent import get_db_session
        from services.variant_service import list_variants as service_list_variants
        
        db = get_db_session()
        if not db:
            return {"error": "no_db_session"}
        
        variants = service_list_variants(db, product_code)
        
        if not variants:
            return {
                "success": False,
                "message": f"محصول با کد '{product_code}' یافت نشد یا هیچ گونه‌ای ندارد"
            }
        
        return {
            "success": True,
            "product_code": product_code,
            "variants": variants,
            "message": f"تعداد {len(variants)} گونه برای محصول {product_code} یافت شد"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "خطا در دریافت گونه‌های محصول"
        }

@tool
def get_variant_by_sku(sku_code: str) -> dict:
    """Get variant details by SKU code.
    
    Args:
        sku_code: SKU code (e.g., "A0001-BLK-350ML")
    
    Returns:
        dict with variant details
    """
    try:
        from .agent import get_db_session
        from services.variant_service import get_variant_by_sku as service_get_variant_by_sku
        
        db = get_db_session()
        if not db:
            return {"error": "no_db_session"}
        
        variant = service_get_variant_by_sku(db, sku_code)
        
        if not variant:
            return {
                "success": False,
                "message": f"گونه با کد '{sku_code}' یافت نشد"
            }
        
        return {
            "success": True,
            "variant": variant,
            "message": f"گونه {sku_code} یافت شد"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "خطا در دریافت جزئیات گونه"
        }

@tool
def find_variants(product_code: str, attributes: dict) -> dict:
    """Find variants by product code and attributes.
    
    Args:
        product_code: Product code (e.g., "A0001")
        attributes: Dictionary of attributes (e.g., {"color": "black", "size": "L"})
    
    Returns:
        dict with exact match and nearest matches
    """
    try:
        from .agent import get_db_session
        from services.variant_service import find_variants as service_find_variants
        
        db = get_db_session()
        if not db:
            return {"error": "no_db_session"}
        
        exact_match, nearest_matches = service_find_variants(db, product_code, attributes)
        
        return {
            "success": True,
            "product_code": product_code,
            "attributes": attributes,
            "exact_match": exact_match,
            "nearest_matches": nearest_matches,
            "message": f"جستجو برای {product_code} با مشخصات {attributes} انجام شد"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "خطا در جستجوی گونه‌ها"
        }