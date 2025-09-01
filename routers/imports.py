"""
Import router for handling CSV/XLSX product imports.
Provides category-scoped preview and commit endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from database import get_db
from models import Category, Product
from services.category_service import get_category_by_id
from services.import_service import (
    read_table, normalize_columns, validate_rows, 
    get_validation_summary, create_product_payload
)
from services.product_service import create_product
from schemas.product import ProductCreate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/products/preview")
async def preview_product_import(
    category_id: int = Query(..., description="Category ID for all imported products"),
    file: UploadFile = File(..., description="CSV or Excel file"),
    db: Session = Depends(get_db)
):
    """
    Preview product import from CSV/Excel file.
    
    All products will be imported under the specified category.
    Returns preview with row-by-row validation.
    """
    # Validate category_id is provided
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id is required"
        )
    
    # Validate category exists
    category = get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    try:
        # Read and parse file
        df = read_table(file)
        
        # Normalize column names
        df = normalize_columns(df)
        
        # Validate required columns exist
        from services.import_service import REQUIRED_COLUMNS
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Validate rows
        validation_results = validate_rows(df)
        
        # Limit rows to first 200 for payload safety
        limited_results = validation_results[:200]
        
        # Get summary
        summary = get_validation_summary(validation_results)
        
        return {
            "category_id": category_id,
            "total": summary["total"],
            "valid": summary["valid"],
            "invalid": summary["invalid"],
            "rows": limited_results
        }
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="pandas/openpyxl not installed. Please install: pip install pandas openpyxl"
        )
    except Exception as e:
        logger.error(f"Error in preview import: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/products")
async def import_products(
    category_id: int = Query(..., description="Category ID for all imported products"),
    file: UploadFile = File(..., description="CSV or Excel file"),
    db: Session = Depends(get_db)
):
    """
    Import products from CSV/Excel file.
    
    All products will be imported under the specified category.
    Products are created using product_service.create_product to ensure proper code generation.
    """
    # Validate category_id is provided
    if not category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category_id is required"
        )
    
    # Validate category exists
    category = get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    try:
        # Read and parse file
        df = read_table(file)
        
        # Normalize column names
        df = normalize_columns(df)
        
        # Validate required columns exist
        from services.import_service import REQUIRED_COLUMNS
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Validate all rows first
        validation_results = validate_rows(df)
        
        # Check if any rows are invalid
        invalid_rows = [r for r in validation_results if not r["valid"]]
        if invalid_rows:
            invalid_count = len(invalid_rows)
            total_count = len(validation_results)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Found {invalid_count} invalid rows out of {total_count}. "
                       f"Please fix all validation errors before importing."
            )
        
        # Import valid products
        inserted = 0
        errors = []
        
        for result in validation_results:
            try:
                # Create product payload
                product_data = create_product_payload(result["data"], category_id)
                
                # Create product using product service (ensures code generation)
                product_create = ProductCreate(**product_data)
                create_product(db, product_create)
                
                inserted += 1
                
            except Exception as e:
                error_msg = f"Row {result['row_index']}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return {
            "inserted": inserted,
            "skipped": 0,
            "errors": errors,
            "category_id": category_id
        }
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="pandas/openpyxl not installed. Please install: pip install pandas openpyxl"
        )
    except Exception as e:
        logger.error(f"Error in product import: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/products/template.csv")
async def download_template_csv():
    """
    Download a template CSV file with proper headers for product import.
    """
    template_content = """name,price,stock,description,image_url,tags,is_active
Sample Product 1,99.99,10,This is a sample product description,https://example.com/image1.jpg,sample,test,true
Sample Product 2,149.99,5,Another sample product,https://example.com/image2.jpg,sample,premium,true
Sample Product 3,29.99,20,Basic product example,https://example.com/image3.jpg,basic,simple,false"""
    
    return {
        "filename": "product_import_template.csv",
        "content": template_content,
        "content_type": "text/csv"
    }
