# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Helper utilities for test scripts
"""

import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

def json_dump_pretty(data: Dict[str, Any], indent: int = 2) -> str:
    """Pretty print JSON with proper encoding"""
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except Exception as e:
        return f"JSON serialization error: {e}"

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get nested dictionary value using dot notation"""
    keys = key.split('.')
    current = data
    
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    
    return current

def today_iso() -> str:
    """Get today's date in ISO format (YYYY-MM-DD)"""
    return datetime.now().strftime("%Y-%m-%d")

def yesterday_iso() -> str:
    """Get yesterday's date in ISO format (YYYY-MM-DD)"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def make_request(method: str, url: str, data: Optional[Dict] = None, **kwargs) -> requests.Response:
    """Make HTTP request with error handling"""
    import requests
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, **kwargs)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, **kwargs)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data, **kwargs)
        elif method.upper() == "DELETE":
            response = requests.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP request failed: {e}")

def print_success(message: str):
    """Print success message with green formatting"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message with red formatting"""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message with yellow formatting"""
    print(f"⚠️  {message}")

def print_info(message: str):
    """Print info message with blue formatting"""
    print(f"ℹ️  {message}")

def exit_success(message: str = "Success"):
    """Exit with success status"""
    print_success(message)
    sys.exit(0)

def exit_failure(message: str = "Failure"):
    """Exit with failure status"""
    print_error(message)
    sys.exit(1)

def check_required_fields(data: Dict[str, Any], required_fields: list[str]) -> list[str]:
    """Check if required fields exist in data, return missing fields"""
    missing = []
    for field in required_fields:
        if field not in data:
            missing.append(field)
    return missing

def format_currency(amount: float) -> str:
    """Format currency amount with Persian number formatting"""
    # Simple Persian number mapping
    persian_numbers = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    
    amount_str = f"{amount:,.0f}"
    for eng, persian in persian_numbers.items():
        amount_str = amount_str.replace(eng, persian)
    
    return f"{amount_str} تومان"

def format_date(date_obj: datetime) -> str:
    """Format date in Persian-friendly format"""
    return date_obj.strftime("%Y/%m/%d %H:%M")

def wait_for_backend(url: str, max_attempts: int = 30, delay: float = 1.0) -> bool:
    """Wait for backend to become available"""
    import requests
    import time
    
    print_info("Waiting for backend to become available...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success("Backend is available!")
                return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
            time.sleep(delay)
    
    print_error("Backend did not become available in time")
    return False 