import os
import sqlite3

# Ensure the database directory exists
db_path = "database/data.db"
schema_path = "database/schema.sql"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Connect to SQLite (creates the file if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Read schema.sql and execute it
with open(schema_path, "r") as schema_file:
    schema_sql = schema_file.read()
    cursor.executescript(schema_sql)

# Commit changes and close connection
conn.commit()
conn.close()

print(f"✅ Database initialized from {schema_path} into {db_path}")
