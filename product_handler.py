import logging
import re
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from models import Product, Category
from database import get_db
from schemas import ProductCreate, ProductUpdate, ProductOut
from services.product_service import create_product as create_product_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["products"])


def validate_image_url(image_url: str) -> bool:
    """Validate that image_url is a valid URL ending with allowed extensions."""
    if not image_url:
        return True  # Allow empty image_url
    
    # Check if it's a valid URL ending with allowed extensions
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.svg')
    
    # Remove query parameters for validation
    url_without_query = image_url.split('?')[0].lower()
    
    # Check if URL ends with allowed extension
    if any(url_without_query.endswith(ext) for ext in allowed_extensions):
        return True
    
    # Also allow common placeholder services
    if any(service in image_url.lower() for service in ['placehold.co', 'via.placeholder.com', 'placeholder.com']):
        return True
    
    return False


def validate_sizes(sizes: List[str]) -> bool:
    """Validate that sizes is a list of strings."""
    if not isinstance(sizes, list):
        return False
    return all(isinstance(size, str) for size in sizes)


@router.get("/", response_model=List[ProductOut])
def get_products(
    q: Optional[str] = Query(None, description="Search query for name, code, or category"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    in_stock_only: Optional[bool] = Query(None, description="Filter to show only in-stock products"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    sort: Optional[str] = Query("created_at", description="Sort field: created_at, price, stock, name, code"),
    order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Number of products to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of products to skip"),
    page: Optional[int] = Query(None, ge=1, description="Page number (1-based)"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Get products with search, filtering, and pagination.
    
    Supports both limit/offset and page/page_size pagination styles.
    """
    # Handle pagination - page/page_size takes precedence over limit/offset
    if page is not None and page_size is not None:
        limit = min(page_size, 100)  # Cap at 100
        offset = (page - 1) * page_size
    else:
        # Use limit/offset if page/page_size not provided
        limit = limit or 20
        offset = offset or 0
    
    logger.info(f"📦 Fetching products with query='{q}', category_id={category_id}, limit={limit}, offset={offset}")
    
    # Build query with category relationship
    query = db.query(Product).options(joinedload(Product.category))
    
    # Apply search filter
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.code.ilike(search_term),
                Product.category.has(Category.name.ilike(search_term))
            )
        )
    
    # Apply category filter
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    # Apply active status filter
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    # Apply stock filter
    if in_stock_only:
        query = query.filter(Product.stock > 0)
    
    # Apply price filters
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Apply sorting
    sort_field = getattr(Product, sort, Product.created_at)
    if order == "asc":
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())
    
    # Apply pagination
    products = query.offset(offset).limit(limit).all()
    
    logger.info(f"✅ Found {len(products)} products")
    
    # Convert database products to response format
    response_products = []
    for product in products:
        # Handle sizes - check if it exists in the model, otherwise use empty list
        sizes_list = []
        if hasattr(product, 'sizes') and product.sizes is not None:
            sizes_list = product.sizes.split(",")
        
        # Handle thumbnail_url - check if it exists in the model
        thumbnail_url = None
        if hasattr(product, 'thumbnail_url'):
            thumbnail_url = product.thumbnail_url
            
        # Calculate low_stock status
        low_stock = product.stock <= (product.low_stock_threshold or 5)
        
        response_data = {
            "id": product.id,
            "code": product.code,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "sizes": sizes_list,
            "image_url": product.image_url,
            "thumbnail_url": thumbnail_url,
            "stock": product.stock,
            "low_stock": low_stock,
            "low_stock_threshold": product.low_stock_threshold or 5,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else "Unknown",
            "tags": product.tags,
            "is_active": product.is_active,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }
        response_products.append(ProductOut(**response_data))
    
    return response_products


@router.get("/chatbot", response_model=List[dict])
def get_products_for_chatbot(
    q: Optional[str] = Query(None, description="Search query for name, code, or category"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="Number of products to return"),
    db: Session = Depends(get_db)
):
    """
    Get products for chatbot integration.
    
    Returns simplified product data optimized for chatbot responses.
    This endpoint is read-only and requires no authentication (dev only).
    
    Returns:
        List[dict]: Simplified product data with fields: code, name, price, stock, category, image
    """
    # Build query with category relationship
    query = db.query(Product).options(joinedload(Product.category))
    
    # Apply search filter
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.code.ilike(search_term),
                Product.category.has(Category.name.ilike(search_term))
            )
        )
    
    # Apply category filter
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    # Apply limit and get results
    products = query.limit(limit).all()
    
    # Return simplified data for chatbot
    return [
        {
            "code": product.code,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
            "category": product.category.name if product.category else "Unknown",
            "image": product.thumbnail_url or product.image_url or None,
        }
        for product in products
    ]


def search_products_by_name(db: Session, query: str) -> List[Product]:
    """
    Search for products by name or description.
    
    Args:
        db: Database session
        query: Search query string
        
    Returns:
        List[Product]: List of matching products
    """
    try:
        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower()
        
        # Split query into words for better matching
        search_terms = query_lower.split()
        
        # Build dynamic query
        db_query = db.query(Product)
        
        # Search in name and description
        conditions = []
        for term in search_terms:
            conditions.append(
                or_(
                    Product.name.ilike(f"%{term}%"),
                    Product.description.ilike(f"%{term}%")
                )
            )
        
        if conditions:
            db_query = db_query.filter(or_(*conditions))
        
        # Filter by stock availability (if stock is tracked)
        db_query = db_query.filter(
            or_(Product.stock.is_(None), Product.stock > 0)
        )
        
        # Order by creation date (newest first)
        products = db_query.order_by(Product.created_at.desc()).limit(10).all()
        
        logger.info(f"🔍 Found {len(products)} products for query: '{query}'")
        return products
        
    except Exception as e:
        logger.error(f"❌ Error searching products: {str(e)}")
        return []


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    logger.info(f"📥 New product received: {product.name}")
    logger.info(f"🧪 Full product payload: {product.dict()}")
    
    try:
        # Validate category_id is provided
        if not product.category_id:
            logger.error("❌ Product validation failed: category_id is required")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="category_id required"
            )
        
        # Validate category exists
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            logger.error(f"❌ Product validation failed: category with ID {product.category_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="category not found"
            )
        
        # Validate sizes field
        if not validate_sizes(product.sizes):
            logger.error(f"❌ Product validation failed: sizes must be a list of strings")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="فیلد سایزها باید یک لیست از رشته‌ها باشد"
            )
        
        # Validate image_url
        if not validate_image_url(product.image_url):
            logger.error(f"❌ Product validation failed: invalid image URL format")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="آدرس تصویر نامعتبر است. فقط فرمت‌های jpg، jpeg، png و gif مجاز هستند"
            )
        
        # Use the product service to create the product (handles code generation and all required fields)
        created_product = create_product_service(db, product)
        
        logger.info(f"✅ Product created successfully with ID: {created_product.id}")
        return created_product
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"❌ Product creation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"خطا در ایجاد محصول: {str(e)}"
        )

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """
    Update a product by ID (full update).
    
    Args:
        product_id: The ID of the product to update
        product: ProductUpdate schema with fields to update
        db: Database session
        
    Returns:
        ProductOut: Updated product data
        
    Raises:
        HTTPException 404: Product not found
    """
    logger.info(f"📝 Updating product with ID: {product_id}")
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        logger.error(f"❌ Product not found with ID: {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get the update data, excluding unset fields
    update_data = product.dict(exclude_unset=True)
    
    # For each field in ProductUpdate, update the field if a new value is provided
    for field, value in update_data.items():
        if field == "sizes" and value is not None:
            # Handle sizes field - convert list to string for database storage
            if isinstance(value, list):
                sizes_str = ",".join(value)
                setattr(db_product, field, sizes_str)
                logger.info(f"✅ Updated {field}: {value} -> {sizes_str}")
            else:
                logger.warning(f"⚠️ Invalid sizes format: {value}")
        else:
            setattr(db_product, field, value)
            logger.info(f"✅ Updated {field}: {value}")
    
    # Commit changes to database
    db.commit()
    db.refresh(db_product)
    
    logger.info(f"✅ Product {product_id} updated successfully")
    
    # Convert sizes string back to list for response
    sizes_list = db_product.sizes.split(",") if db_product.sizes is not None else []
    
    # Create response data
    response_data = {
        "id": db_product.id,
        "name": db_product.name,
        "description": db_product.description,
        "price": db_product.price,
        "sizes": sizes_list,
        "image_url": db_product.image_url,
        "stock": db_product.stock,
        "created_at": db_product.created_at
    }
    
    return ProductOut(**response_data)


@router.patch("/{product_id}", response_model=ProductOut)
def patch_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """
    Partially update a product by ID.
    
    Args:
        product_id: The ID of the product to update
        product: ProductUpdate schema with fields to update
        db: Database session
        
    Returns:
        ProductOut: Updated product data
        
    Raises:
        HTTPException 404: Product not found
    """
    logger.info(f"📝 Patching product with ID: {product_id}")
    
    # Fetch product by ID from the database
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        logger.error(f"❌ Product not found with ID: {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get the update data, excluding unset fields
    update_data = product.dict(exclude_unset=True)
    
    # For each field in ProductUpdate, update the field if a new value is provided
    for field, value in update_data.items():
        if field == "sizes" and value is not None:
            # Handle sizes field - convert list to string for database storage
            if isinstance(value, list):
                sizes_str = ",".join(value)
                setattr(db_product, field, sizes_str)
                logger.info(f"✅ Updated {field}: {value} -> {sizes_str}")
            else:
                logger.warning(f"⚠️ Invalid sizes format: {value}")
        else:
            setattr(db_product, field, value)
            logger.info(f"✅ Updated {field}: {value}")
    
    # Commit changes to database
    db.commit()
    db.refresh(db_product)
    
    logger.info(f"✅ Product {product_id} patched successfully")
    
    # Convert sizes string back to list for response
    sizes_list = db_product.sizes.split(",") if db_product.sizes is not None else []
    
    # Create response data
    response_data = {
        "id": db_product.id,
        "name": db_product.name,
        "description": db_product.description,
        "price": db_product.price,
        "sizes": sizes_list,
        "image_url": db_product.image_url,
        "stock": db_product.stock,
        "created_at": db_product.created_at
    }
    
    return ProductOut(**response_data)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return None 