\c inventory_db;

CREATE TYPE category_enum AS ENUM ('food', 'clothes', 'accessories', 'electronics');

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category category_enum NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    description TEXT,
    stock_count INTEGER DEFAULT 0 CHECK (stock_count >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_category_price ON items(category, price);
CREATE INDEX idx_stock_count ON items(stock_count);