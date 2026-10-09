-- Demo dataset for the Semantic SQL PoC.
-- Build: sqlite3 demo/demo.db < demo/seed.sql

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    segment TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (id),
    total NUMERIC(10, 2) NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

INSERT INTO customers (id, name, segment, created_at) VALUES
    (1, 'Acme Corp', 'Enterprise', '2025-11-03 09:00:00'),
    (2, 'Globex', 'Enterprise', '2026-01-15 10:30:00'),
    (3, 'Initech', 'SMB', '2026-02-20 14:00:00'),
    (4, 'Umbrella Ltd', 'SMB', '2026-03-05 08:45:00'),
    (5, 'Hooli', 'Enterprise', '2026-04-11 16:20:00'),
    (6, 'Jane Doe', 'Consumer', '2026-05-02 12:00:00'),
    (7, 'John Smith', 'Consumer', '2026-06-18 18:10:00'),
    (8, 'Stark Supplies', 'SMB', '2026-07-22 11:05:00');

INSERT INTO orders (id, customer_id, total, status, created_at) VALUES
    (1, 1, 12000.00, 'completed', '2026-07-02 10:00:00'),
    (2, 2, 8500.00, 'completed', '2026-07-09 11:30:00'),
    (3, 3, 950.00, 'completed', '2026-07-15 09:15:00'),
    (4, 6, 120.00, 'cancelled', '2026-07-20 19:40:00'),
    (5, 4, 1800.00, 'completed', '2026-07-28 13:00:00'),
    (6, 5, 15000.00, 'completed', '2026-08-03 15:45:00'),
    (7, 7, 89.99, 'completed', '2026-08-07 20:05:00'),
    (8, 1, 9800.00, 'completed', '2026-08-14 10:10:00'),
    (9, 8, 2300.00, 'cancelled', '2026-08-19 14:30:00'),
    (10, 3, 1100.00, 'completed', '2026-08-25 09:50:00'),
    (11, 2, 7600.00, 'completed', '2026-09-01 08:30:00'),
    (12, 6, 45.50, 'completed', '2026-09-04 21:15:00'),
    (13, 4, 2100.00, 'completed', '2026-09-09 12:40:00'),
    (14, 5, 13250.00, 'completed', '2026-09-12 16:00:00'),
    (15, 7, 210.00, 'cancelled', '2026-09-15 18:25:00'),
    (16, 8, 3400.00, 'completed', '2026-09-18 10:05:00'),
    (17, 1, 11000.00, 'completed', '2026-09-22 11:20:00'),
    (18, 3, 780.00, 'completed', '2026-09-26 15:35:00'),
    (19, 6, 64.00, 'completed', '2026-09-29 20:50:00'),
    (20, 2, 9100.00, 'pending', '2026-10-01 09:00:00'),
    (21, 4, 1950.00, 'completed', '2026-10-03 13:15:00'),
    (22, 5, 14100.00, 'pending', '2026-10-05 14:45:00'),
    (23, 7, 99.00, 'completed', '2026-10-06 19:30:00'),
    (24, 8, 2750.00, 'completed', '2026-10-07 10:40:00');
