"""
Variant API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from database import get_db
from services.variant_service import (
    list_variants,
    get_variant_by_sku,
    find_variants,
    create_variant,
    get_legacy_mapping
)

router = APIRouter(tags=["variants"])

class VariantOut(BaseModel):
    id: int
    sku_code: str
    attributes: Dict[str, Any]
    price_override: Optional[float] = None
    stock_qty: int
    is_active: bool
    effective_price: float

class VariantCreateIn(BaseModel):
    sku_code: str
    attributes: Dict[str, Any]
    price_override: Optional[float] = None
    stock_qty: int = 0

class FindVariantsIn(BaseModel):
    attributes: Dict[str, Any]

@router.get("/products/code/{product_code}/variants", response_model=List[VariantOut])
def list_product_variants(product_code: str, db: Session = Depends(get_db)):
    """List all variants for a product"""
    variants = list_variants(db, product_code)
    if not variants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with code '{product_code}' not found or has no variants"
        )
    return variants

@router.get("/sku/{sku_code}", response_model=VariantOut)
def get_variant_by_sku_endpoint(sku_code: str, db: Session = Depends(get_db)):
    """Get variant by SKU code"""
    variant = get_variant_by_sku(db, sku_code)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant with SKU '{sku_code}' not found"
        )
    return variant

@router.post("/products/code/{product_code}/find", response_model=Dict[str, Any])
def find_variants_endpoint(
    product_code: str, 
    payload: FindVariantsIn, 
    db: Session = Depends(get_db)
):
    """Find variants by product code and attributes"""
    exact_match, nearest_matches = find_variants(db, product_code, payload.attributes)
    
    return {
        "exact_match": exact_match,
        "nearest_matches": nearest_matches,
        "query": {
            "product_code": product_code,
            "attributes": payload.attributes
        }
    }

@router.post("/products/code/{product_code}/variants", response_model=VariantOut, status_code=status.HTTP_201_CREATED)
def create_variant_endpoint(
    product_code: str,
    payload: VariantCreateIn,
    db: Session = Depends(get_db)
):
    """Create a new variant for a product"""
    variant = create_variant(
        db=db,
        product_code=product_code,
        sku_code=payload.sku_code,
        attributes=payload.attributes,
        price_override=payload.price_override,
        stock_qty=payload.stock_qty
    )
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create variant. SKU might already exist or product not found."
        )
    
    return variant

@router.get("/legacy-mapping", response_model=Dict[str, str])
def get_legacy_mapping_endpoint(
    product_code: str,
    color: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Legacy mapping: {product_code, color, size} -> sku_code"""
    sku_code = get_legacy_mapping(db, product_code, color, size)
    
    if not sku_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No variant found for product '{product_code}' with color='{color}', size='{size}'"
        )
    
    return {
        "product_code": product_code,
        "color": color,
        "size": size,
        "sku_code": sku_code
    }
