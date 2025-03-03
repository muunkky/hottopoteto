-- Drop old tables (use with caution)
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS logs;

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
