-- 客戶
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL
);

-- 商品
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
);

-- 訂單
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers (id),
    status TEXT NOT NULL CHECK (
        status IN (
            'pending',
            'shipped',
            'delayed',
            'done'
        )
    ),
    amount REAL NOT NULL,
    order_date TEXT NOT NULL, -- 下單日 YYYY-MM-DD
    due_date TEXT NOT NULL -- 應出貨日 YYYY-MM-DD
);

-- 訂單品項(一張訂單有多個商品)
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders (id),
    product_id INTEGER NOT NULL REFERENCES products (id),
    quantity INTEGER NOT NULL
);