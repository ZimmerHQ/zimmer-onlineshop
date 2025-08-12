from datetime import datetime
from typing import Optional
from models import FallbackQuestion
from sqlalchemy.orm import Session

def log_fallback(user_id: int, question: str, db: Session) -> None:
    """
    Log fallback questions to the database.
    Creates a new FallbackQuestion record for unprocessed user questions.
    """
    try:
        # Create a new FallbackQuestion with user_id and question
        new_fallback = FallbackQuestion(
            user_id=user_id,
            question=question
        )
        
        # Add it to the database
        db.add(new_fallback)
        
        # Commit the session
        db.commit()
        
    except Exception as e:
        print(f"Error logging fallback question: {e}")
        # Don't re-raise the exception since this function returns None
