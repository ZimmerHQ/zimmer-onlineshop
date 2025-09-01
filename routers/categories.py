from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
import os

from database import get_db
from schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from services.category_service import create_category, list_categories, get_category_by_id, update_category, update_category_with_prefix
from models import Category, Product

router = APIRouter(tags=["categories"])


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new category with auto-assigned prefix.
    
    The prefix will be automatically assigned based on existing categories:
    - First category: 'A'
    - Second category: 'B'
    - And so on...
    """
    return create_category(db, category.name)


@router.get("/", response_model=List[CategoryOut])
def list_categories_endpoint(db: Session = Depends(get_db)):
    """
    List all categories ordered by creation date.
    
    Returns categories with their assigned prefixes.
    """
    return list_categories(db)


@router.get("/exists")
def check_categories_exist(db: Session = Depends(get_db)):
    """
    Check if any categories exist.
    
    Returns:
        dict: {"exists": bool}
    """
    count = db.query(Category).count()
    return {"exists": count > 0}


@router.get("/summary")
def get_categories_summary(db: Session = Depends(get_db)):
    """
    Get categories with product counts for dashboard display.
    
    Returns:
        List[dict]: Categories with product counts
    """
    # Query categories with product counts
    categories_with_counts = db.query(
        Category.id,
        Category.name,
        Category.prefix,
        func.count(Product.id).label('product_count')
        ).outerjoin(Product).group_by(Category.id, Category.name, Category.prefix).all()
    
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "prefix": cat.prefix,
            "product_count": cat.product_count
        }
        for cat in categories_with_counts
    ]


@router.get("/{category_id}", response_model=CategoryOut)
def get_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    """
    Get a specific category by ID.
    """
    category = get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category_patch_endpoint(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a category name and/or prefix.
    
    Rules:
    - name must be unique
    - prefix must be 1-2 uppercase letters [A-Z]{1,2}
    - Changing prefix does NOT retroactively rewrite existing product codes
    - Only affects NEW products created after the change
    """
    return update_category_with_prefix(db, category_id, category_update)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category_endpoint(
    category_id: int,
    category_update: CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Update a category name.
    """
    return update_category(db, category_id, category_update.name)


@router.delete("/{category_id}")
def delete_category_endpoint(
    category_id: int,
    force: bool = Query(False, description="Force delete even if category has products"),
    db: Session = Depends(get_db)
):
    """
    Delete a category by ID.
    
    DEV ONLY: This endpoint is only available in development environment.
    
    Args:
        force: If True, delete category even if it has products (cascading delete)
    """
    # Check if we're in production
    if os.getenv("ENV") == "prod":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DELETE endpoint not available in production"
        )
    
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )
        
        # Check if category has products
        product_count = db.query(Product).filter(Product.category_id == category_id).count()
        
        if product_count > 0 and not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category has {product_count} products. Use ?force=true to delete anyway."
            )
        
        # If force is True, delete all products in this category first
        if force and product_count > 0:
            db.query(Product).filter(Product.category_id == category_id).delete()
        
        db.delete(category)
        db.commit()
        
        return {"message": f"Category {category_id} deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete category: {str(e)}"
        ) 