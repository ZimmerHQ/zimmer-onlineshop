-- Add CRM tables and update orders table
-- Migration: Add Customer table and CRM fields to Order table

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(80) NOT NULL,
  last_name VARCHAR(80) NOT NULL,
  phone VARCHAR(32) NOT NULL UNIQUE,
  address TEXT NOT NULL,
  postal_code VARCHAR(20) NOT NULL,
  notes TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Add indexes for customers table
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_postal_code ON customers(postal_code);

-- Add CRM fields to orders table
ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_id INTEGER NULL REFERENCES customers(id);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS customer_snapshot JSONB NULL;

-- Add index for customer_id in orders
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);

-- Update existing orders to have basic customer snapshot
UPDATE orders 
SET customer_snapshot = jsonb_build_object(
  'first_name', split_part(customer_name, ' ', 1),
  'last_name', CASE 
    WHEN position(' ' in customer_name) > 0 
    THEN substring(customer_name from position(' ' in customer_name) + 1)
    ELSE ''
  END,
  'phone', customer_phone,
  'address', COALESCE(customer_address, ''),
  'postal_code', '',
  'notes', COALESCE(customer_notes, '')
)
WHERE customer_snapshot IS NULL;
