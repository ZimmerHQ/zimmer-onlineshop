#!/usr/bin/env python3
"""
Migration script to add Telegram integration tables
"""

import logging
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database import engine, get_db
from models import TelegramConfig, TelegramUser, TelegramMessage, FAQ, SalesReport
from models import Base as MainBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_telegram_tables():
    """Create Telegram-related tables"""
    try:
        logger.info("🔧 Creating Telegram tables...")
        
        # Create all Telegram tables
        TelegramBase.metadata.create_all(bind=engine)
        
        # Create main tables (in case they don't exist)
        MainBase.metadata.create_all(bind=engine)
        
        logger.info("✅ Telegram tables created successfully")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        expected_tables = [
            'telegram_configs',
            'telegram_users', 
            'telegram_messages',
            'faqs',
            'sales_reports'
        ]
        
        existing_tables = inspector.get_table_names()
        logger.info(f"📋 Existing tables: {existing_tables}")
        
        for table in expected_tables:
            if table in existing_tables:
                logger.info(f"✅ Table {table} exists")
                
                # Show table structure
                columns = inspector.get_columns(table)
                logger.info(f"   Columns in {table}:")
                for col in columns:
                    logger.info(f"     - {col['name']}: {col['type']}")
            else:
                logger.error(f"❌ Table {table} missing")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating Telegram tables: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        logger.info("🔧 Creating sample data...")
        
        db = next(get_db())
        
        # Create sample FAQ
        # FAQ already imported above
        from datetime import datetime
        
        sample_faqs = [
            {
                'question': 'چطور می‌تونم محصولی رو سفارش بدم؟',
                'answer': 'برای سفارش محصول، ابتدا کد محصول را پیدا کنید و سپس با شماره تماس ما تماس بگیرید.',
                'tags': 'سفارش,خرید,محصول',
                'is_active': True
            },
            {
                'question': 'آیا امکان ارسال به شهرستان وجود دارد؟',
                'answer': 'بله، ما به تمام شهرهای ایران ارسال داریم. هزینه ارسال بر اساس شهر مقصد محاسبه می‌شود.',
                'tags': 'ارسال,شهرستان,هزینه',
                'is_active': True
            },
            {
                'question': 'چطور می‌تونم موجودی محصول رو چک کنم؟',
                'answer': 'برای بررسی موجودی، کد محصول را در ربات تلگرام وارد کنید یا با ما تماس بگیرید.',
                'tags': 'موجودی,کد محصول,ربات',
                'is_active': True
            }
        ]
        
        for faq_data in sample_faqs:
            # Check if FAQ already exists
            existing = db.query(FAQ).filter(FAQ.question == faq_data['question']).first()
            if not existing:
                faq = FAQ(**faq_data)
                db.add(faq)
                logger.info(f"✅ Added FAQ: {faq_data['question']}")
        
        db.commit()
        logger.info("✅ Sample data created successfully")
        
    except Exception as e:
        logger.error(f"❌ Error creating sample data: {e}")
        db.rollback()

def main():
    """Main migration function"""
    logger.info("🚀 Starting Telegram migration...")
    
    # Create tables
    if not migrate_telegram_tables():
        logger.error("❌ Migration failed")
        sys.exit(1)
    
    # Create sample data
    create_sample_data()
    
    logger.info("🎉 Migration completed successfully!")
    logger.info("")
    logger.info("📋 Next steps:")
    logger.info("1. Configure your Telegram bot token in the admin panel")
    logger.info("2. Set up webhook URL with your domain")
    logger.info("3. Test the bot connection")
    logger.info("4. Add FAQ entries as needed")

if __name__ == "__main__":
    main() 