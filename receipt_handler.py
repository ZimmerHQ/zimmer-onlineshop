from typing import Optional
from sqlalchemy.orm import Session
from models import Order, Receipt

def handle_receipt(user_id: int, photo_id: str, db: Session) -> str:
    """
    Handle receipt photos.
    Creates a new Receipt record linked to the user's latest pending order.
    """
    try:
        # Query the user's latest order (Order with status "pending")
        latest_order = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status == "pending"
        ).order_by(Order.created_at.desc()).first()
        
        # If no order exists, return error message
        if not latest_order:
            return "سفارشی برای ثبت رسید پیدا نشد."
        
        # Create a new Receipt object with image_url = photo_id, linked to that order
        new_receipt = Receipt(
            order_id=latest_order.id,
            image_url=photo_id,
            verified=False  # Leave verified=False by default
        )
        
        # Add to database and commit
        db.add(new_receipt)
        db.commit()
        
        # Return success message
        return "رسید شما دریافت شد و در حال بررسی است."
    
    except Exception as e:
        print(f"Error processing receipt: {e}")
        # Return Persian error message
        return "مشکلی در ثبت رسید پیش آمد. لطفاً دوباره تلاش کنید."
