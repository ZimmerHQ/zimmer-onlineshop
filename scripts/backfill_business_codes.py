#!/usr/bin/env python3
"""
Backfill script for customer_code and order_code fields.
This script generates codes for existing customers and orders.

Usage:
    python scripts/backfill_business_codes.py

The script is idempotent and can be run multiple times safely.
"""

import sys
import os
from datetime import datetime
from typing import List, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models import Customer, Order, OrderItem
from utils.business_codes import generate_customer_code, generate_order_code
from sqlalchemy import text


def backfill_customer_codes(db, batch_size: int = 100) -> Tuple[int, int]:
    """
    Backfill customer codes for existing customers.
    
    Returns:
        Tuple of (processed_count, error_count)
    """
    processed = 0
    errors = 0
    
    print("🔄 Backfilling customer codes...")
    
    # Get customers without codes
    customers_without_codes = db.query(Customer).filter(
        Customer.customer_code.is_(None)
    ).all()
    
    total_customers = len(customers_without_codes)
    print(f"📊 Found {total_customers} customers without codes")
    
    for i, customer in enumerate(customers_without_codes):
        try:
            # Generate unique code
            code = generate_customer_code(db, customer)
            customer.customer_code = code
            
            processed += 1
            
            if (i + 1) % batch_size == 0:
                db.commit()
                print(f"✅ Processed {i + 1}/{total_customers} customers")
                
        except Exception as e:
            errors += 1
            print(f"❌ Error processing customer {customer.id}: {str(e)}")
            db.rollback()
    
    # Final commit
    db.commit()
    print(f"✅ Customer codes backfill complete: {processed} processed, {errors} errors")
    
    return processed, errors


def backfill_order_codes(db, batch_size: int = 100) -> Tuple[int, int]:
    """
    Backfill order codes for existing orders.
    
    Returns:
        Tuple of (processed_count, error_count)
    """
    processed = 0
    errors = 0
    
    print("🔄 Backfilling order codes...")
    
    # Get orders without codes
    orders_without_codes = db.query(Order).filter(
        Order.order_code.is_(None)
    ).all()
    
    total_orders = len(orders_without_codes)
    print(f"📊 Found {total_orders} orders without codes")
    
    for i, order in enumerate(orders_without_codes):
        try:
            # Generate unique code
            code = generate_order_code(db, order)
            order.order_code = code
            
            processed += 1
            
            if (i + 1) % batch_size == 0:
                db.commit()
                print(f"✅ Processed {i + 1}/{total_orders} orders")
                
        except Exception as e:
            errors += 1
            print(f"❌ Error processing order {order.id}: {str(e)}")
            db.rollback()
    
    # Final commit
    db.commit()
    print(f"✅ Order codes backfill complete: {processed} processed, {errors} errors")
    
    return processed, errors


def backfill_order_item_product_codes(db, batch_size: int = 100) -> Tuple[int, int]:
    """
    Backfill product_code field in order items.
    
    Returns:
        Tuple of (processed_count, error_count)
    """
    processed = 0
    errors = 0
    
    print("🔄 Backfilling order item product codes...")
    
    # Get order items without product_code
    items_without_codes = db.query(OrderItem).filter(
        OrderItem.product_code.is_(None)
    ).all()
    
    total_items = len(items_without_codes)
    print(f"📊 Found {total_items} order items without product codes")
    
    for i, item in enumerate(items_without_codes):
        try:
            # Get product code from related product
            if item.product:
                item.product_code = item.product.code
                processed += 1
            else:
                # Fallback to product_name if product not found
                item.product_code = f"UNKNOWN-{item.id}"
                processed += 1
                print(f"⚠️  Order item {item.id} has no product, using fallback code")
            
            if (i + 1) % batch_size == 0:
                db.commit()
                print(f"✅ Processed {i + 1}/{total_items} order items")
                
        except Exception as e:
            errors += 1
            print(f"❌ Error processing order item {item.id}: {str(e)}")
            db.rollback()
    
    # Final commit
    db.commit()
    print(f"✅ Order item product codes backfill complete: {processed} processed, {errors} errors")
    
    return processed, errors


def add_unique_constraints(db):
    """Add unique constraints after backfill is complete."""
    print("🔒 Adding unique constraints...")
    
    try:
        # Add unique constraint for customer_code
        db.execute(text("ALTER TABLE customers ADD CONSTRAINT uk_customers_customer_code UNIQUE (customer_code)"))
        print("✅ Added unique constraint for customer_code")
    except Exception as e:
        print(f"⚠️  Customer code unique constraint: {str(e)}")
    
    try:
        # Add unique constraint for order_code
        db.execute(text("ALTER TABLE orders ADD CONSTRAINT uk_orders_order_code UNIQUE (order_code)"))
        print("✅ Added unique constraint for order_code")
    except Exception as e:
        print(f"⚠️  Order code unique constraint: {str(e)}")
    
    db.commit()


def make_columns_not_null(db):
    """Make code columns NOT NULL after backfill and constraints."""
    print("🔒 Making code columns NOT NULL...")
    
    try:
        # Make customer_code NOT NULL
        db.execute(text("ALTER TABLE customers ALTER COLUMN customer_code SET NOT NULL"))
        print("✅ Made customer_code NOT NULL")
    except Exception as e:
        print(f"⚠️  Customer code NOT NULL: {str(e)}")
    
    try:
        # Make order_code NOT NULL
        db.execute(text("ALTER TABLE orders ALTER COLUMN order_code SET NOT NULL"))
        print("✅ Made order_code NOT NULL")
    except Exception as e:
        print(f"⚠️  Order code NOT NULL: {str(e)}")
    
    try:
        # Make order_items.product_code NOT NULL
        db.execute(text("ALTER TABLE order_items ALTER COLUMN product_code SET NOT NULL"))
        print("✅ Made order_items.product_code NOT NULL")
    except Exception as e:
        print(f"⚠️  Order item product code NOT NULL: {str(e)}")
    
    db.commit()


def verify_backfill(db):
    """Verify that backfill was successful."""
    print("🔍 Verifying backfill results...")
    
    # Check customers
    customers_without_codes = db.query(Customer).filter(
        Customer.customer_code.is_(None)
    ).count()
    
    # Check orders
    orders_without_codes = db.query(Order).filter(
        Order.order_code.is_(None)
    ).count()
    
    # Check order items
    items_without_codes = db.query(OrderItem).filter(
        OrderItem.product_code.is_(None)
    ).count()
    
    print(f"📊 Verification results:")
    print(f"   Customers without codes: {customers_without_codes}")
    print(f"   Orders without codes: {orders_without_codes}")
    print(f"   Order items without codes: {items_without_codes}")
    
    if customers_without_codes == 0 and orders_without_codes == 0 and items_without_codes == 0:
        print("✅ Backfill verification successful!")
        return True
    else:
        print("❌ Backfill verification failed!")
        return False


def main():
    """Main backfill function."""
    print("🚀 Starting business codes backfill...")
    print(f"⏰ Started at: {datetime.now()}")
    
    db = SessionLocal()
    
    try:
        # Step 1: Backfill customer codes
        customer_processed, customer_errors = backfill_customer_codes(db)
        
        # Step 2: Backfill order codes
        order_processed, order_errors = backfill_order_codes(db)
        
        # Step 3: Backfill order item product codes
        item_processed, item_errors = backfill_order_item_product_codes(db)
        
        # Step 4: Verify backfill
        if verify_backfill(db):
            # Step 5: Add unique constraints
            add_unique_constraints(db)
            
            # Step 6: Make columns NOT NULL
            make_columns_not_null(db)
            
            print("🎉 Backfill completed successfully!")
        else:
            print("❌ Backfill verification failed. Please check the data.")
            return 1
        
    except Exception as e:
        print(f"💥 Fatal error during backfill: {str(e)}")
        db.rollback()
        return 1
    
    finally:
        db.close()
    
    print(f"⏰ Completed at: {datetime.now()}")
    return 0


if __name__ == "__main__":
    exit(main())
