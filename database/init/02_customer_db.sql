\c customer_db;

CREATE TYPE gender_enum AS ENUM ('male', 'female', 'other');
CREATE TYPE marital_status_enum AS ENUM ('single', 'married', 'divorced', 'widowed');

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    age INTEGER CHECK (age > 0),
    address TEXT,
    gender gender_enum,
    marital_status marital_status_enum,
    wallet_balance DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);