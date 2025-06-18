-- Create sample tables for testing the MCP PostgreSQL agent

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

-- Insert sample data
INSERT INTO users (username, email, password_hash) VALUES
    ('john_doe', 'john@example.com', 'hash123'),
    ('jane_smith', 'jane@example.com', 'hash456'),
    ('bob_wilson', 'bob@example.com', 'hash789'),
    ('alice_brown', 'alice@example.com', 'hash101'),
    ('charlie_davis', 'charlie@example.com', 'hash202');

INSERT INTO products (name, description, price, stock_quantity, category) VALUES
    ('Laptop', 'High-performance laptop', 999.99, 10, 'Electronics'),
    ('Mouse', 'Wireless mouse', 29.99, 50, 'Electronics'),
    ('Keyboard', 'Mechanical keyboard', 79.99, 25, 'Electronics'),
    ('Monitor', '24-inch LED monitor', 199.99, 15, 'Electronics'),
    ('Headphones', 'Noise-canceling headphones', 149.99, 30, 'Electronics'),
    ('Coffee Mug', 'Ceramic coffee mug', 12.99, 100, 'Home & Kitchen'),
    ('Notebook', 'Spiral notebook', 5.99, 200, 'Office Supplies'),
    ('Pen Set', 'Set of 10 pens', 8.99, 75, 'Office Supplies');

INSERT INTO orders (user_id, total_amount, status) VALUES
    (1, 1029.98, 'completed'),
    (2, 209.98, 'completed'),
    (3, 149.99, 'pending'),
    (1, 42.98, 'completed'),
    (4, 999.99, 'shipped'),
    (5, 25.97, 'completed');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 999.99),
    (1, 2, 1, 29.99),
    (2, 4, 1, 199.99),
    (2, 3, 1, 79.99),
    (3, 5, 1, 149.99),
    (4, 6, 2, 12.99),
    (4, 7, 3, 5.99),
    (5, 1, 1, 999.99),
    (6, 8, 1, 8.99),
    (6, 7, 1, 5.99),
    (6, 6, 1, 10.99);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_products_category ON products(category); 