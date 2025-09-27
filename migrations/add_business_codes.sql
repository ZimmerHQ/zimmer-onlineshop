-- Migration: Add business codes for customers and orders
-- This migration adds customer_code and order_code columns with proper indexing
-- Following the pattern: nullable -> backfill -> unique index -> NOT NULL

-- Step 1: Add nullable columns
ALTER TABLE customers ADD COLUMN customer_code VARCHAR(50) NULL;
ALTER TABLE orders ADD COLUMN order_code VARCHAR(50) NULL;

-- Step 2: Add indexes for performance (before backfill)
CREATE INDEX idx_customers_customer_code ON customers(customer_code);
CREATE INDEX idx_orders_order_code ON orders(order_code);

-- Note: Backfill will be done by Python script
-- Step 3: After backfill, add unique constraints
-- ALTER TABLE customers ADD CONSTRAINT uk_customers_customer_code UNIQUE (customer_code);
-- ALTER TABLE orders ADD CONSTRAINT uk_orders_order_code UNIQUE (order_code);

-- Step 4: After unique constraints, make columns NOT NULL
-- ALTER TABLE customers ALTER COLUMN customer_code SET NOT NULL;
-- ALTER TABLE orders ALTER COLUMN order_code SET NOT NULL;
