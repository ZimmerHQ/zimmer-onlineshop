from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ImportPreviewRow(BaseModel):
    row_index: int
    valid: bool
    errors: List[str]
    data: Dict[str, Any]


class ImportPreviewResponse(BaseModel):
    rows: List[ImportPreviewRow]
    suggested_mapping: Dict[str, str]
    total_rows: int
    valid_rows: int
    invalid_rows: int


class ImportResult(BaseModel):
    inserted: int
    skipped: int
    errors: List[str]
    total_processed: int 