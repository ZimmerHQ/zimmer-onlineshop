from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
from models import Product
from services.product_service import (
    list_products, 
    get_product, 
    create_product, 
    update_product, 
    search_products_by_name,
    get_product_details,
    get_product_by_code
)
from schemas.product import ProductCreate, ProductUpdate, ProductOut, ProductSearchResult, ProductDetails

router = APIRouter(tags=["products"])


@router.get("/search", response_model=List[ProductSearchResult])
def search_products_endpoint(
    q: Optional[str] = Query(None, description="Search query (name, code, or category)"),
    code: Optional[str] = Query(None, description="Product code for exact match"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Search products for chatbot suggestions.
    
    - Use `q` for general search (name, code, category)
    - Use `code` for exact code match (prioritized)
    - Use `category_id` to filter by category
    - Returns minimal info for suggestions
    """
    return search_products_by_name(db, q, limit)


@router.get("/code/{code}", response_model=ProductDetails)
def get_product_by_code_endpoint(code: str, db: Session = Depends(get_db)):
    """
    Get product details by code for Q&A.
    
    Returns full product information including variants, sizes, colors, and stock.
    Useful for questions like "سایز دارید؟ قیمت چنده؟"
    """
    product = get_product_by_code(db, code)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with code '{code}' not found"
        )
    
    return get_product_details(db, product.id)


@router.get("/id/{product_id}", response_model=ProductDetails)
def get_product_by_id_endpoint(product_id: int, db: Session = Depends(get_db)):
    """
    Get product details by ID for Q&A.
    
    Returns full product information including variants, sizes, colors, and stock.
    Useful for questions like "سایز دارید؟ قیمت چنده؟"
    """
    product_details = get_product_details(db, product_id)
    if not product_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return product_details


@router.get("/", response_model=List[ProductOut])
def get_products(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    q: Optional[str] = Query(None, description="Search query"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    in_stock_only: Optional[bool] = Query(None, description="Only show products with stock > 0"),
    low_stock_only: Optional[bool] = Query(None, description="Only show products with low stock"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    sort: Optional[str] = Query(None, description="Sort field (created_at, price, stock, name, code)"),
    order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    Get products with enhanced filtering, search, and sorting.
    
    - Use `category_id` to filter by category
    - Use `q` to search by name, code, or category
    - Use `in_stock_only` to show only products with available stock
    - Use `low_stock_only` to show products below threshold
    - Use `min_price` and `max_price` for price range filtering
    - Use `sort` and `order` for sorting
    - Use `limit` and `offset` for pagination
    """
    products, total_count = list_products(
        db=db,
        category_id=category_id,
        q=q,
        is_active=is_active,
        in_stock_only=in_stock_only,
        low_stock_only=low_stock_only,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        order=order,
        limit=limit,
        offset=offset
    )
    
    return products


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.
    """
    return create_product(db, product)


@router.put("/{product_id}", response_model=ProductOut)
def update_product_endpoint(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """
    Update an existing product.
    """
    return update_product(db, product_id, product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    """
    Delete a product.
    """
    # Get the raw Product model for deletion
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    try:
        # First delete any order items referencing this product
        from models import OrderItem
        order_items = db.query(OrderItem).filter(OrderItem.product_id == product_id).all()
        for item in order_items:
            db.delete(item)
        
        # Now delete the product (variants will be deleted automatically due to cascade)
        db.delete(product)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}"
        ) 