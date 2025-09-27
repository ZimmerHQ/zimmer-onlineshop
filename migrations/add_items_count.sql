-- Add items_count column to orders table
ALTER TABLE orders ADD COLUMN items_count INTEGER DEFAULT 0;
