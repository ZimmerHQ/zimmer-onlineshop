from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List

from models import Category
from schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from utils.category_prefix import assign_next_category_prefix


def create_category(db: Session, name: str) -> CategoryOut:
    """
    Creates a new category with auto-assigned prefix.
    
    Args:
        db: Database session
        name: Category name
        
    Returns:
        CategoryOut: Created category
        
    Raises:
        HTTPException: If name already exists or prefix assignment fails
    """
    try:
        # Check if category name already exists
        existing = db.query(Category).filter(Category.name == name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with name '{name}' already exists"
            )
        
        # Assign next available prefix
        prefix = assign_next_category_prefix(db)
        
        # Create category
        category = Category(name=name, prefix=prefix)
        db.add(category)
        db.commit()
        db.refresh(category)
        
        return CategoryOut.from_orm(category)
        
    except IntegrityError as e:
        db.rollback()
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with name '{name}' already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


def list_categories(db: Session) -> List[CategoryOut]:
    """
    Lists all categories ordered by creation date.
    
    Args:
        db: Database session
        
    Returns:
        List[CategoryOut]: List of categories
    """
    categories = db.query(Category).order_by(Category.created_at).all()
    return [CategoryOut.from_orm(category) for category in categories]


def get_category_by_id(db: Session, category_id: int) -> Category:
    """
    Gets a category by ID.
    
    Args:
        db: Database session
        category_id: Category ID
        
    Returns:
        Category: Category model
        
    Raises:
        HTTPException: If category not found
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    return category


def get_category_by_name(db: Session, name: str) -> Category:
    """
    Gets a category by name.
    
    Args:
        db: Database session
        name: Category name
        
    Returns:
        Category: Category model or None if not found
    """
    return db.query(Category).filter(Category.name == name).first()


def update_category(db: Session, category_id: int, name: str) -> CategoryOut:
    """
    Updates a category name.
    
    Args:
        db: Database session
        category_id: Category ID
        name: New category name
        
    Returns:
        CategoryOut: Updated category
        
    Raises:
        HTTPException: If category not found or name already exists
    """
    try:
        # Get existing category
        category = get_category_by_id(db, category_id)
        
        # Check if new name already exists (excluding current category)
        existing = db.query(Category).filter(
            Category.name == name,
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category with name '{name}' already exists"
            )
        
        # Update category name
        category.name = name
        db.commit()
        db.refresh(category)
        
        return CategoryOut.from_orm(category)
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


def update_category_with_prefix(db: Session, category_id: int, category_update: CategoryUpdate) -> CategoryOut:
    """
    Updates a category name and/or prefix with validation.
    
    Args:
        db: Database session
        category_id: Category ID
        category_update: CategoryUpdate object with name and/or prefix
        
    Returns:
        CategoryOut: Updated category
        
    Raises:
        HTTPException: If category not found, name already exists, or prefix already exists
    """
    try:
        # Get existing category
        category = get_category_by_id(db, category_id)
        
        # Update name if provided
        if category_update.name is not None:
            # Check if new name already exists (excluding current category)
            existing = db.query(Category).filter(
                Category.name == category_update.name,
                Category.id != category_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Category with name '{category_update.name}' already exists"
                )
            category.name = category_update.name
        
        # Update prefix if provided
        if category_update.prefix is not None:
            # Check if new prefix already exists (excluding current category)
            existing = db.query(Category).filter(
                Category.prefix == category_update.prefix,
                Category.id != category_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Category with prefix '{category_update.prefix}' already exists"
                )
            category.prefix = category_update.prefix
        
        db.commit()
        db.refresh(category)
        
        return CategoryOut.from_orm(category)
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        ) 