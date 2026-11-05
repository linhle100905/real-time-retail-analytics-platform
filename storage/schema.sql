-- storage/schema.sql

-- Drop tables if they exist
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS product_metrics;
DROP TABLE IF EXISTS customers;

-- Customers table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    country VARCHAR(100),
    age INT,
    gender VARCHAR(20),
    membership_tier VARCHAR(50),
    registration_date TIMESTAMP,
    total_orders INT,
    total_spend_usd FLOAT,
    avg_order_value_usd FLOAT,
    days_since_last_purchase INT,
    preferred_category VARCHAR(100),
    preferred_device VARCHAR(50),
    preferred_payment_method VARCHAR(50),
    acquisition_channel VARCHAR(100),
    reviews_given INT,
    avg_review_score FLOAT,
    returns_made INT,
    wishlist_items INT,
    newsletter_subscribed INT,
    churned INT
);

-- Products table (Metrics)
CREATE TABLE product_metrics (
    product_id VARCHAR(100) PRIMARY KEY,
    views INT,
    carts INT,
    removes INT,
    purchases INT,
    purchase_value FLOAT,
    unique_users INT,
    latest_price FLOAT,
    conversion_rate FLOAT,
    brand VARCHAR(100),
    category_code VARCHAR(255)
);

-- Orders table
CREATE TABLE orders (
    order_id VARCHAR(100) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_date TIMESTAMP,
    year INT,
    month INT,
    quarter VARCHAR(10),
    day_of_week VARCHAR(20),
    product_name VARCHAR(255),
    category VARCHAR(100),
    unit_price_usd FLOAT,
    quantity INT,
    subtotal_usd FLOAT,
    discount_pct FLOAT,
    discount_amount_usd FLOAT,
    shipping_fee_usd FLOAT,
    tax_pct FLOAT,
    tax_amount_usd FLOAT,
    total_amount_usd FLOAT,
    payment_method VARCHAR(50),
    device_used VARCHAR(50),
    delivery_days INT,
    delivery_date TIMESTAMP,
    order_status VARCHAR(50),
    returned INT,
    customer_rating FLOAT,
    session_duration_minutes FLOAT,
    pages_viewed_before_purchase INT,
    is_repeat_customer INT,
    country VARCHAR(100),
    age INT,
    gender VARCHAR(20),
    membership_tier VARCHAR(50),
    churned INT
);
