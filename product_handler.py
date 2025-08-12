import logging
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from models import Product
from database import get_db
from schemas import ProductCreate, ProductUpdate, ProductOut

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
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    
    # Convert database products to response format
    response_products = []
    for product in products:
        sizes_list = product.sizes.split(",") if product.sizes is not None else []
        response_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "sizes": sizes_list,
            "image_url": product.image_url,
            "thumbnail_url": product.thumbnail_url,
            "stock": product.stock,
            "created_at": product.created_at
        }
        response_products.append(ProductOut(**response_data))
    
    return response_products


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
        
        # Convert sizes list to string for database storage
        sizes_str = ",".join(product.sizes)
        
        # Create database product object
        db_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            sizes=sizes_str,
            image_url=product.image_url,
            thumbnail_url=product.thumbnail_url,
            stock=product.stock
        )
        
        # Save to database
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        logger.info(f"✅ Product saved with ID: {db_product.id}")
        
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
            "thumbnail_url": db_product.thumbnail_url,
            "stock": db_product.stock,
            "created_at": db_product.created_at
        }
        
        return ProductOut(**response_data)
        
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