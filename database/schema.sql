-- Drop old tables (use with caution)
DROP TABLE IF EXISTS ice_cream_flavors;
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS flavors;

-- Create the ice cream flavors table
CREATE TABLE ice_cream_flavors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flavor_name TEXT NOT NULL,
    description TEXT,
    inspiration TEXT,
    demographic TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create a records table to match data_query.sql
CREATE TABLE records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id TEXT NOT NULL,
    data TEXT
);

-- Create a users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

-- Create a logs table
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create a flavors table
CREATE TABLE flavors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flavor_name TEXT NOT NULL
);

-- Insert sample ice cream flavors
INSERT INTO ice_cream_flavors (flavor_name, description, inspiration, demographic) VALUES 
    ('Vanilla Dream', 'A classic vanilla with a dreamy, creamy texture', 'vanilla', 'everyone'),
    ('Chocolate Thunder', 'Rich chocolate ice cream with fudge swirls', 'chocolate', 'chocolate lovers'),
    ('Berry Blast', 'Mixed berry explosion with real fruit chunks', 'berries', 'fruit enthusiasts');

-- Insert test data into records table
INSERT INTO records (record_id, data) VALUES 
    ('rec1', 'Test data 1'),
    ('rec2', 'Test data 2'),
    ('rec3', 'Test data 3');

-- Insert test data into users table
INSERT INTO users (name, email) VALUES 
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com');

-- Insert test data into logs table
INSERT INTO logs (event) VALUES 
    ('Event 1'),
    ('Event 2'),
    ('Event 3');