-- Add variants system to products
-- Migration: add_variants_system.sql

-- 1. Add attribute_schema to products table
ALTER TABLE products ADD COLUMN attribute_schema JSON;

-- 2. Create product_variants table
CREATE TABLE product_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_code VARCHAR(50) UNIQUE NOT NULL,
    product_id INTEGER NOT NULL,
    attributes JSON NOT NULL DEFAULT '{}',
    price_override DECIMAL(10,2) NULL,
    stock_qty INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 3. Create indexes for performance
CREATE INDEX idx_product_variants_sku_code ON product_variants(sku_code);
CREATE INDEX idx_product_variants_product_id ON product_variants(product_id);
CREATE INDEX idx_product_variants_is_active ON product_variants(is_active);

-- 4. Add unique constraint on (product_id, attributes_hash)
-- We'll use a deterministic hash of the attributes JSON
-- For SQLite, we'll create a trigger to maintain this
CREATE TRIGGER tr_product_variants_attributes_hash
    AFTER INSERT ON product_variants
    FOR EACH ROW
    WHEN NEW.attributes IS NOT NULL
BEGIN
    -- This is a simplified hash - in production you might want a more robust hash
    UPDATE product_variants 
    SET attributes_hash = hex(sha1(NEW.attributes)) 
    WHERE id = NEW.id;
END;

-- Add attributes_hash column for the unique constraint
ALTER TABLE product_variants ADD COLUMN attributes_hash VARCHAR(64);

-- Create unique index on (product_id, attributes_hash)
CREATE UNIQUE INDEX uk_product_variants_product_attributes 
    ON product_variants(product_id, attributes_hash);

-- 5. Update order_items to support variants
ALTER TABLE order_items ADD COLUMN sku_code VARCHAR(50);
ALTER TABLE order_items ADD COLUMN variant_attributes_snapshot JSON;
ALTER TABLE order_items ADD COLUMN unit_price_snapshot DECIMAL(10,2);

-- Create index on sku_code for order_items
CREATE INDEX idx_order_items_sku_code ON order_items(sku_code);
