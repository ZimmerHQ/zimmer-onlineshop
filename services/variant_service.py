"""
Variant Service Layer
Handles product variants, SKU resolution, and inventory management
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import Product, ProductVariant
import json
import hashlib

def generate_attributes_hash(attributes: Dict[str, Any]) -> str:
    """Generate a deterministic hash for attributes"""
    if not attributes:
        return hashlib.sha1(b'{}').hexdigest()
    
    # Sort keys to ensure consistent hashing
    sorted_attrs = json.dumps(attributes, sort_keys=True)
    return hashlib.sha1(sorted_attrs.encode()).hexdigest()

def list_variants(db: Session, product_code: str) -> List[Dict[str, Any]]:
    """List all variants for a product"""
    product = db.query(Product).filter(Product.code == product_code.upper()).first()
    if not product:
        return []
    
    variants = db.query(ProductVariant).filter(
        and_(
            ProductVariant.product_id == product.id,
            ProductVariant.is_active == True
        )
    ).all()
    
    result = []
    for variant in variants:
        result.append({
            "id": variant.id,
            "sku_code": variant.sku_code,
            "attributes": variant.attributes or {},
            "price_override": float(variant.price_override) if variant.price_override else None,
            "stock_qty": variant.stock_qty,
            "is_active": variant.is_active,
            "effective_price": get_effective_price(variant, product)
        })
    
    return result

def get_variant_by_sku(db: Session, sku_code: str) -> Optional[Dict[str, Any]]:
    """Get variant by SKU code"""
    variant = db.query(ProductVariant).filter(
        and_(
            ProductVariant.sku_code == sku_code.upper(),
            ProductVariant.is_active == True
        )
    ).first()
    
    if not variant:
        return None
    
    product = db.query(Product).filter(Product.id == variant.product_id).first()
    if not product:
        return None
    
    return {
        "id": variant.id,
        "sku_code": variant.sku_code,
        "product_id": variant.product_id,
        "product_code": product.code,
        "product_name": product.name,
        "attributes": variant.attributes or {},
        "price_override": float(variant.price_override) if variant.price_override else None,
        "stock_qty": variant.stock_qty,
        "is_active": variant.is_active,
        "effective_price": get_effective_price(variant, product)
    }

def find_variants(db: Session, product_code: str, attributes: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Find variants by product code and attributes.
    Returns (exact_match, nearest_matches)
    """
    product = db.query(Product).filter(Product.code == product_code.upper()).first()
    if not product:
        return None, []
    
    # First, try to find exact match
    attributes_hash = generate_attributes_hash(attributes)
    exact_variant = db.query(ProductVariant).filter(
        and_(
            ProductVariant.product_id == product.id,
            ProductVariant.attributes_hash == attributes_hash,
            ProductVariant.is_active == True
        )
    ).first()
    
    if exact_variant:
        exact_match = {
            "id": exact_variant.id,
            "sku_code": exact_variant.sku_code,
            "attributes": exact_variant.attributes or {},
            "price_override": float(exact_variant.price_override) if exact_variant.price_override else None,
            "stock_qty": exact_variant.stock_qty,
            "is_active": exact_variant.is_active,
            "effective_price": get_effective_price(exact_variant, product)
        }
    else:
        exact_match = None
    
    # Find nearest matches (variants with some matching attributes)
    all_variants = db.query(ProductVariant).filter(
        and_(
            ProductVariant.product_id == product.id,
            ProductVariant.is_active == True
        )
    ).all()
    
    nearest_matches = []
    for variant in all_variants:
        if variant.attributes:
            # Calculate similarity score
            variant_attrs = variant.attributes
            matching_attrs = 0
            total_attrs = len(attributes)
            
            for key, value in attributes.items():
                if key in variant_attrs and variant_attrs[key] == value:
                    matching_attrs += 1
            
            if matching_attrs > 0:
                similarity_score = matching_attrs / total_attrs
                nearest_matches.append({
                    "id": variant.id,
                    "sku_code": variant.sku_code,
                    "attributes": variant.attributes or {},
                    "price_override": float(variant.price_override) if variant.price_override else None,
                    "stock_qty": variant.stock_qty,
                    "is_active": variant.is_active,
                    "effective_price": get_effective_price(variant, product),
                    "similarity_score": similarity_score
                })
    
    # Sort by similarity score
    nearest_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return exact_match, nearest_matches

def get_effective_price(variant: ProductVariant, product: Product) -> float:
    """Get the effective price for a variant (product price + override)"""
    base_price = float(product.price)
    if variant.price_override is not None:
        return float(variant.price_override)
    return base_price

def reserve_stock(db: Session, sku_code: str, quantity: int) -> bool:
    """Reserve stock for a variant"""
    variant = db.query(ProductVariant).filter(
        ProductVariant.sku_code == sku_code.upper()
    ).first()
    
    if not variant:
        return False
    
    if variant.stock_qty < quantity:
        return False
    
    variant.stock_qty -= quantity
    db.commit()
    return True

def release_stock(db: Session, sku_code: str, quantity: int) -> bool:
    """Release reserved stock for a variant"""
    variant = db.query(ProductVariant).filter(
        ProductVariant.sku_code == sku_code.upper()
    ).first()
    
    if not variant:
        return False
    
    variant.stock_qty += quantity
    db.commit()
    return True

def consume_stock(db: Session, sku_code: str, quantity: int) -> bool:
    """Consume stock for a variant (permanent reduction)"""
    variant = db.query(ProductVariant).filter(
        ProductVariant.sku_code == sku_code.upper()
    ).first()
    
    if not variant:
        return False
    
    if variant.stock_qty < quantity:
        return False
    
    variant.stock_qty -= quantity
    db.commit()
    return True

def create_variant(db: Session, product_code: str, sku_code: str, attributes: Dict[str, Any], 
                  price_override: Optional[float] = None, stock_qty: int = 0) -> Optional[Dict[str, Any]]:
    """Create a new variant for a product"""
    product = db.query(Product).filter(Product.code == product_code.upper()).first()
    if not product:
        return None
    
    # Check if SKU already exists
    existing_sku = db.query(ProductVariant).filter(
        ProductVariant.sku_code == sku_code.upper()
    ).first()
    
    if existing_sku:
        return None
    
    # Check if variant with same attributes already exists
    attributes_hash = generate_attributes_hash(attributes)
    existing_variant = db.query(ProductVariant).filter(
        and_(
            ProductVariant.product_id == product.id,
            ProductVariant.attributes_hash == attributes_hash
        )
    ).first()
    
    if existing_variant:
        return None
    
    # Create the variant
    variant = ProductVariant(
        sku_code=sku_code.upper(),
        product_id=product.id,
        attributes=attributes,
        price_override=price_override,
        stock_qty=stock_qty,
        is_active=True,
        attributes_hash=attributes_hash
    )
    
    db.add(variant)
    db.commit()
    db.refresh(variant)
    
    return {
        "id": variant.id,
        "sku_code": variant.sku_code,
        "product_id": variant.product_id,
        "product_code": product.code,
        "attributes": variant.attributes or {},
        "price_override": float(variant.price_override) if variant.price_override else None,
        "stock_qty": variant.stock_qty,
        "is_active": variant.is_active,
        "effective_price": get_effective_price(variant, product)
    }

def get_legacy_mapping(db: Session, product_code: str, color: Optional[str] = None, size: Optional[str] = None) -> Optional[str]:
    """
    Legacy mapping function for backward compatibility.
    Maps {product_code, color, size} -> sku_code
    """
    product = db.query(Product).filter(Product.code == product_code.upper()).first()
    if not product:
        return None
    
    # Build attributes from legacy parameters
    attributes = {}
    if color:
        attributes['color'] = color
    if size:
        attributes['size'] = size
    
    # Find matching variant
    exact_match, _ = find_variants(db, product_code, attributes)
    if exact_match:
        return exact_match['sku_code']
    
    return None
