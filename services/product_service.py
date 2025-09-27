from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
import json
import logging

from models import Product, Category, ProductVariant
from schemas.product import ProductCreate, ProductUpdate, ProductOut, ProductSearchResult, ProductDetails, VariantCreate, VariantUpdate, VariantOut
from utils.product_code import generate_code_for_category
from utils.normalization import clean_labels, clean_attributes, extract_product_code, extract_attributes_from_query
from services.category_service import get_category_by_id


def get_product_by_code(db: Session, code: str) -> Optional[Product]:
    """Get product by code."""
    return db.query(Product).filter(Product.code == code).first()

def get_by_code(db: Session, code: str) -> Optional[Product]:
    """Alias for get_product_by_code for compatibility."""
    return get_product_by_code(db, code)


def get_product_details(db: Session, product_id: int) -> Optional[ProductDetails]:
    """Get full product details with variants for Q&A."""
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.variants)
    ).filter(Product.id == product_id).first()
    
    if not product:
        return None
    
    # Calculate total stock
    total_stock = product.stock
    if product.variants:
        total_stock = sum(v.stock for v in product.variants)
    
    # Prepare variants
    variants = []
    for variant in product.variants:
        variants.append(VariantOut(
            id=variant.id,
            product_id=variant.product_id,
            size=variant.size,
            color=variant.color,
            sku=variant.sku,
            stock=variant.stock,
            price_delta=variant.price_delta,
            created_at=variant.created_at,
            updated_at=variant.updated_at
        ))
    
    # Prepare images
    images = []
    if product.thumbnail_url:
        images.append(product.thumbnail_url)
    if product.image_url:
        images.append(product.image_url)
    
    # Parse structured attributes
    available_sizes = []
    available_colors = []
    
    if product.available_sizes_json:
        try:
            available_sizes = json.loads(product.available_sizes_json)
        except (json.JSONDecodeError, TypeError):
            available_sizes = []
    
    if product.available_colors_json:
        try:
            available_colors = json.loads(product.available_colors_json)
        except (json.JSONDecodeError, TypeError):
            available_colors = []
    
    return ProductDetails(
        id=product.id,
        code=product.code,
        name=product.name,
        description=product.description,
        price=product.price,
        total_stock=total_stock,
        category={
            "id": product.category.id,
            "name": product.category.name,
            "prefix": product.category.prefix
        },
        images=images,
        variants=variants,
        variants_count=len(variants),
        available_sizes=available_sizes,
        available_colors=available_colors,
        tags=product.tags
    )


def search_products_by_name(db: Session, query: str, limit: int = 20) -> List[ProductSearchResult]:
    """Search products by name, code, or description."""
    search_term = f"%{query}%"
    products = db.query(Product).options(joinedload(Product.category)).filter(
        or_(
            Product.name.ilike(search_term),
            Product.code.ilike(search_term),
            Product.description.ilike(search_term)
        )
    ).filter(Product.is_active == True).limit(limit).all()
    
    return [
        ProductSearchResult(
            id=product.id,
            code=product.code,
            name=product.name,
            price=product.price,
            total_stock=product.stock,
            category_name=product.category.name if product.category else "",
            thumbnail_url=product.thumbnail_url
        )
        for product in products
    ]

def search_products(db: Session, q: Optional[str] = None, code: Optional[str] = None, 
                   category_id: Optional[int] = None, limit: int = 5) -> List[Product]:
    """Robust search function that handles different search modes."""
    query = db.query(Product).options(joinedload(Product.category))
    
    # Code-first search
    if code:
        query = query.filter(Product.code == code)
    elif q:
        # Text search
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.code.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    # Category filter
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # Only active products
    query = query.filter(Product.is_active == True)
    
    # Execute and log results
    products = query.limit(limit).all()
    logging.info(f"🔍 Search: q='{q}', code='{code}', category_id={category_id}, found={len(products)}")
    
    return products


def create_product(db: Session, payload: ProductCreate) -> ProductOut:
    """
    Creates a new product with auto-generated code.
    
    Args:
        db: Database session
        payload: Product creation data
        
    Returns:
        ProductOut: Created product with category name
        
    Raises:
        HTTPException: If category doesn't exist or code generation fails
    """
    # Validate category exists
    category = get_category_by_id(db, payload.category_id)
    
    # Try to create product with retry logic for code conflicts
    max_retries = 5
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Generate unique product code
            code = generate_code_for_category(db, payload.category_id)
            
            # Prepare structured attributes
            available_sizes_json = None
            available_colors_json = None
            labels_json = None
            attributes_json = None
            
            if payload.available_sizes:
                available_sizes_json = json.dumps(payload.available_sizes)
            if payload.available_colors:
                available_colors_json = json.dumps(payload.available_colors)
            if payload.labels:
                labels_json = json.dumps(clean_labels(payload.labels))
            if payload.attributes:
                attributes_json = json.dumps(clean_attributes(payload.attributes))
            
            # Create product
            product = Product(
                name=payload.name,
                description=payload.description,
                price=payload.price,
                stock=payload.stock,
                low_stock_threshold=payload.low_stock_threshold or 5,
                code=code,
                category_id=payload.category_id,
                image_url=payload.image_url,
                thumbnail_url=payload.thumbnail_url,
                sizes=','.join(payload.sizes) if payload.sizes else None,
                available_sizes_json=available_sizes_json,
                available_colors_json=available_colors_json,
                labels_json=labels_json,
                attributes_json=attributes_json,
                tags=payload.tags,
                is_active=payload.is_active
            )
            
            db.add(product)
            db.commit()
            db.refresh(product)
            
            return to_product_out(product)
            
        except IntegrityError as e:
            db.rollback()
            last_error = e
            
            # Check if it's a code conflict
            if "UNIQUE constraint failed" in str(e) and "code" in str(e):
                if attempt < max_retries - 1:
                    # Try again with a fresh code generation
                    continue
                else:
                    # Max retries reached
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to generate unique product code after {max_retries} attempts. Please try again."
                    )
            else:
                # Other integrity constraint violation
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Product creation failed due to constraint violation"
                )
                
        except ValueError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # This should never be reached
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unexpected error in product creation"
    )


def update_product(db: Session, product_id: int, payload: ProductUpdate) -> ProductOut:
    """
    Updates a product. Does not change the product code.
    
    Args:
        db: Database session
        product_id: Product ID
        payload: Update data
        
    Returns:
        ProductOut: Updated product
        
    Raises:
        HTTPException: If product not found or category doesn't exist
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Validate category if being changed
    if payload.category_id is not None and payload.category_id != product.category_id:
        get_category_by_id(db, payload.category_id)
    
    # Update fields
    update_data = payload.dict(exclude_unset=True)
    
    # Handle sizes field conversion (list to string)
    if 'sizes' in update_data and update_data['sizes'] is not None:
        update_data['sizes'] = ','.join(update_data['sizes'])
    
    # Handle structured attributes
    if 'available_sizes' in update_data and update_data['available_sizes'] is not None:
        update_data['available_sizes_json'] = json.dumps(update_data['available_sizes'])
        del update_data['available_sizes']
    
    if 'available_colors' in update_data and update_data['available_colors'] is not None:
        update_data['available_colors_json'] = json.dumps(update_data['available_colors'])
        del update_data['available_colors']
    
    # Handle new fields
    if 'labels' in update_data and update_data['labels'] is not None:
        update_data['labels_json'] = json.dumps(clean_labels(update_data['labels']))
        del update_data['labels']
    
    if 'attributes' in update_data and update_data['attributes'] is not None:
        update_data['attributes_json'] = json.dumps(clean_attributes(update_data['attributes']))
        del update_data['attributes']
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    try:
        db.commit()
        db.refresh(product)
        return to_product_out(product)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Update failed due to constraint violation"
        )


def get_product(db: Session, product_id: int) -> ProductOut:
    """
    Gets a product by ID with category information.
    
    Args:
        db: Database session
        product_id: Product ID
        
    Returns:
        ProductOut: Product with category name
        
    Raises:
        HTTPException: If product not found
    """
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.variants)
    ).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return to_product_out(product)


def list_products(
    db: Session, 
    category_id: Optional[int] = None, 
    q: Optional[str] = None, 
    is_active: Optional[bool] = None,
    in_stock_only: Optional[bool] = None,
    low_stock_only: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: Optional[str] = None,
    order: Optional[str] = None,
    limit: int = 50, 
    offset: int = 0
) -> tuple[List[ProductOut], int]:
    """
    Lists products with enhanced filtering, search, and sorting.
    
    Args:
        db: Database session
        category_id: Filter by category ID
        q: Search query (name, code, or category)
        is_active: Filter by active status
        in_stock_only: When True, only show products with stock > 0
        low_stock_only: When True, only show products with stock < low_stock_threshold
        min_price: Minimum price filter
        max_price: Maximum price filter
        sort: Sort field (created_at, price, stock, name, code)
        order: Sort order (asc, desc)
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        List[ProductOut]: List of products
    """
    query = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.variants)
    )
    
    # Apply filters
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    if in_stock_only:
        # Check both product stock and variant stock
        query = query.filter(
            or_(
                Product.stock > 0,
                Product.variants.any(ProductVariant.stock > 0)
            )
        )
    
    if low_stock_only:
        query = query.filter(Product.stock < Product.low_stock_threshold)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
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
    
    # Apply sorting
    if sort:
        if sort == "created_at":
            sort_field = Product.created_at
        elif sort == "price":
            sort_field = Product.price
        elif sort == "stock":
            sort_field = Product.stock
        elif sort == "name":
            sort_field = Product.name
        elif sort == "code":
            sort_field = Product.code
        else:
            sort_field = Product.created_at
        
        if order == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
    else:
        # Default sorting
        query = query.order_by(Product.created_at.desc())
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    products = query.offset(offset).limit(limit).all()
    
    # Convert to ProductOut
    product_outs = [to_product_out(product) for product in products]
    
    return product_outs, total_count


def to_product_out(product: Product) -> ProductOut:
    """Convert Product model to ProductOut schema."""
    # Calculate total stock
    total_stock = product.stock
    if product.variants:
        total_stock = sum(v.stock for v in product.variants)
    
    # Prepare variants
    variants = []
    for variant in product.variants:
        variants.append(VariantOut(
            id=variant.id,
            product_id=variant.product_id,
            size=variant.size,
            color=variant.color,
            sku=variant.sku,
            stock=variant.stock,
            price_delta=variant.price_delta,
            created_at=variant.created_at,
            updated_at=variant.updated_at
        ))
    
    # Process sizes field (legacy)
    sizes = []
    if product.sizes:
        sizes = [s.strip() for s in product.sizes.split(',') if s.strip()]
    
    # Process structured attributes
    available_sizes = []
    available_colors = []
    labels = []
    attributes = {}
    
    if product.available_sizes_json:
        try:
            available_sizes = json.loads(product.available_sizes_json)
        except (json.JSONDecodeError, TypeError):
            available_sizes = []
    
    if product.available_colors_json:
        try:
            available_colors = json.loads(product.available_colors_json)
        except (json.JSONDecodeError, TypeError):
            available_colors = []
    
    if product.labels_json:
        try:
            labels = json.loads(product.labels_json)
        except (json.JSONDecodeError, TypeError):
            labels = []
    
    if product.attributes_json:
        try:
            attributes = json.loads(product.attributes_json)
        except (json.JSONDecodeError, TypeError):
            attributes = {}
    
    return ProductOut(
        id=product.id,
        code=product.code,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        low_stock=product.stock <= product.low_stock_threshold,
        low_stock_threshold=product.low_stock_threshold,
        category_id=product.category_id,
        category_name=product.category.name,
        image_url=product.image_url,
        thumbnail_url=product.thumbnail_url,
        tags=product.tags,
        labels=labels,
        attributes=attributes,
        sizes=sizes,
        available_sizes=available_sizes,
        available_colors=available_colors,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
        variants=variants,
        total_stock=total_stock,
        variants_count=len(variants)
    )


# Variant management functions
def create_variant(db: Session, payload: VariantCreate) -> VariantOut:
    """Create a new product variant."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    variant = ProductVariant(**payload.dict())
    db.add(variant)
    db.commit()
    db.refresh(variant)
    
    return VariantOut(
        id=variant.id,
        product_id=variant.product_id,
        size=variant.size,
        color=variant.color,
        sku=variant.sku,
        stock=variant.stock,
        price_delta=variant.price_delta,
        created_at=variant.created_at,
        updated_at=variant.updated_at
    )


def update_variant(db: Session, variant_id: int, payload: VariantUpdate) -> VariantOut:
    """Update a product variant."""
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )
    
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(variant, field, value)
    
    db.commit()
    db.refresh(variant)
    
    return VariantOut(
        id=variant.id,
        product_id=variant.product_id,
        size=variant.size,
        color=variant.color,
        sku=variant.sku,
        stock=variant.stock,
        price_delta=variant.price_delta,
        created_at=variant.created_at,
        updated_at=variant.updated_at
    )


def delete_variant(db: Session, variant_id: int) -> bool:
    """Delete a product variant."""
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )
    
    db.delete(variant)
    db.commit()
    return True 