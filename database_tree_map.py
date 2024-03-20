import sqlite3

def extract_schema(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Fetch tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema = {}
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [(col[1], col[2]) for col in columns]  # Store column names and types
    
    conn.close()
    return schema

def generate_dbml(schema):
    for table, columns in schema.items():
        print(f"Table {table} {{")

        # Print columns
        for column in columns:
            print(f"  {column[0]} {column[1]}")
        
        print("}")

    # Print References
    print("")

    for table, columns in schema.items():
        for column in columns:
            if column[1] == "integer" and column[0].endswith("_id"):
                referenced_table = column[0].replace("_id", "s")
                print(f"Ref: {table}.{column[0]} > {referenced_table}.id")

if __name__ == "__main__":
    database_path = "db.sqlite3"
    schema = extract_schema(database_path)
    generate_dbml(schema)
