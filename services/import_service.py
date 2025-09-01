"""
Import service for handling CSV/XLSX product imports.
Provides validation, parsing, and data normalization functions.
"""

import pandas as pd
import io
from typing import List, Dict, Any, Optional, Tuple
from fastapi import UploadFile, HTTPException, status
import logging

logger = logging.getLogger(__name__)

# File size limit: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Column aliases for common variations
COLUMN_ALIASES = {
    "qty": "stock",
    "quantity": "stock",
    "amount": "price",
    "cost": "price",
    "title": "name",
    "product_name": "name",
    "product": "name",
    "desc": "description",
    "img": "image_url",
    "image": "image_url",
    "thumbnail": "thumbnail_url",
    "thumb": "thumbnail_url",
    "thumb_img": "thumbnail_url",
    "active": "is_active",
    "enabled": "is_active"
}

# Required columns
REQUIRED_COLUMNS = ["name", "price", "stock"]

# Optional columns with defaults
OPTIONAL_COLUMNS = {
    "description": "",
    "image_url": "",
    "thumbnail_url": "",
    "tags": "",
    "is_active": True,
    "low_stock_threshold": 5
}


def detect_file_type(filename: str) -> Optional[str]:
    """Detect file type from filename extension."""
    if not filename:
        return None
    
    filename_lower = filename.lower()
    if filename_lower.endswith('.csv'):
        return "csv"
    elif filename_lower.endswith(('.xlsx', '.xls')):
        return "xlsx"
    return None


def validate_file_size(file: UploadFile) -> None:
    """Validate file size is within limits."""
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file.size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes). "
                   f"Please use a smaller file or split your data."
        )


def read_table(file: UploadFile) -> pd.DataFrame:
    """Read CSV or Excel file into a pandas DataFrame."""
    try:
        # Validate file size
        validate_file_size(file)
        
        # Read file content
        content = file.file.read()
        file.file.seek(0)  # Reset file pointer for potential reuse
        
        file_type = detect_file_type(file.filename)
        if not file_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please use .csv or .xlsx files."
            )
        
        if file_type == "csv":
            # Try different encodings for CSV
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(io.BytesIO(content), encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to read CSV file. Please ensure it's encoded in UTF-8, Latin-1, or CP1252."
                )
        else:  # xlsx
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        
        # Check if DataFrame is empty
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains no data rows."
            )
        
        return df
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File appears to be empty or contains no valid data."
        )
    except Exception as e:
        if "openpyxl" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Excel support not available. Please install: pip install openpyxl"
            )
        elif "pandas" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data processing not available. Please install: pip install pandas"
            )
        else:
            logger.error(f"Error reading file: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading file: {str(e)}"
            )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: lowercase, strip spaces, apply aliases."""
    # Create a copy to avoid modifying original
    df_normalized = df.copy()
    
    # Normalize column names
    normalized_columns = {}
    for col in df_normalized.columns:
        if pd.isna(col):
            continue
            
        # Convert to string, lowercase, strip whitespace
        col_str = str(col).lower().strip()
        
        # Apply aliases
        normalized_name = COLUMN_ALIASES.get(col_str, col_str)
        normalized_columns[col] = normalized_name
    
    # Rename columns
    df_normalized = df_normalized.rename(columns=normalized_columns)
    
    return df_normalized


def validate_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Validate each row and return validation results."""
    validation_results = []
    
    for index, row in df.iterrows():
        row_index = index + 1  # 1-based indexing for user display
        errors = []
        data = {}
        
        # Validate required columns
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
                continue
            
            value = row[col]
            
            if col == "name":
                if pd.isna(value) or str(value).strip() == "":
                    errors.append("Name cannot be empty")
                else:
                    data[col] = str(value).strip()
            
            elif col == "price":
                try:
                    price = float(value)
                    if price < 0:
                        errors.append("Price must be non-negative")
                    else:
                        data[col] = round(price, 2)
                except (ValueError, TypeError):
                    errors.append("Price must be a valid number")
            
            elif col == "stock":
                try:
                    stock = int(float(value))  # Handle cases like 10.0
                    if stock < 0:
                        errors.append("Stock must be non-negative")
                    else:
                        data[col] = stock
                except (ValueError, TypeError):
                    errors.append("Stock must be a valid integer")
        
        # Process optional columns
        for col, default_value in OPTIONAL_COLUMNS.items():
            if col in df.columns:
                value = row[col]
                
                if col == "description":
                    data[col] = str(value).strip() if pd.notna(value) else default_value
                
                elif col == "image_url":
                    data[col] = str(value).strip() if pd.notna(value) else default_value
                
                elif col == "thumbnail_url":
                    data[col] = str(value).strip() if pd.notna(value) else default_value
                
                elif col == "tags":
                    data[col] = str(value).strip() if pd.notna(value) else default_value
                
                elif col == "is_active":
                    if pd.isna(value):
                        data[col] = default_value
                    else:
                        # Handle various boolean representations
                        if isinstance(value, bool):
                            data[col] = value
                        elif isinstance(value, str):
                            data[col] = value.lower() in ['true', '1', 'yes', 'y', 'فعال']
                        elif isinstance(value, (int, float)):
                            data[col] = bool(value)
                        else:
                            data[col] = default_value
                
                elif col == "low_stock_threshold":
                    if pd.isna(value):
                        data[col] = default_value
                    else:
                        try:
                            threshold = int(float(value))
                            if threshold <= 0:
                                errors.append("Low stock threshold must be greater than 0")
                            else:
                                data[col] = threshold
                        except (ValueError, TypeError):
                            errors.append("Low stock threshold must be a valid positive integer")
            else:
                data[col] = default_value
        
        validation_results.append({
            "row_index": row_index,
            "valid": len(errors) == 0,
            "errors": errors,
            "data": data
        })
    
    return validation_results


def get_validation_summary(validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics from validation results."""
    total = len(validation_results)
    valid = sum(1 for result in validation_results if result["valid"])
    invalid = total - valid
    
    return {
        "total": total,
        "valid": valid,
        "invalid": invalid
    }


def create_product_payload(row_data: Dict[str, Any], category_id: int) -> Dict[str, Any]:
    """Create product creation payload from validated row data."""
    return {
        "name": row_data["name"],
        "description": row_data["description"],
        "price": row_data["price"],
        "stock": row_data["stock"],
        "category_id": category_id,
        "image_url": row_data["image_url"],
        "thumbnail_url": row_data["thumbnail_url"],
        "tags": row_data["tags"],
        "is_active": row_data["is_active"]
    }
