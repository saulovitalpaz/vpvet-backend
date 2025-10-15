import psycopg
from psycopg import sql

# Connect to default postgres database to create vpvet database
try:
    # Try to connect to postgres database first
    conn = psycopg.connect("dbname=postgres user=postgres password=postgres host=localhost")
    conn.autocommit = True
    cursor = conn.cursor()

    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'vpvet'")
    exists = cursor.fetchone()

    if exists:
        print("Database 'vpvet' already exists!")
    else:
        # Create database
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier('vpvet')))
        print("Database 'vpvet' created successfully!")

    cursor.close()
    conn.close()

except psycopg.OperationalError as e:
    print(f"Error connecting to PostgreSQL: {e}")
    print("\nPlease ensure:")
    print("1. PostgreSQL is running")
    print("2. Username is 'postgres'")
    print("3. Password is 'postgres' (or update this script)")
    print("4. PostgreSQL is accessible on localhost")
except Exception as e:
    print(f"Error: {e}")
