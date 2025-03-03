import os
import sqlite3
import argparse

def initialize_database(db_path="database/data.db", schema_path="database/schema.sql"):
    if not os.path.exists("database"):
        os.makedirs("database")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute schema.sql to create tables and insert test data
    with open(schema_path, "r") as schema_file:
        schema_sql = schema_file.read()
    cursor.executescript(schema_sql)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize the database.")
    parser.add_argument("--test-data", "-t", action="store_true", help="Include test data in the database.")
    args = parser.parse_args()
    
    initialize_database()
