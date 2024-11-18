import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def check_database_setup():
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='password',
            host='localhost'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Get list of databases
        cur.execute("SELECT datname FROM pg_database;")
        databases = [row[0] for row in cur.fetchall()]

        # Check if our databases exist
        required_dbs = ['customer_db', 'inventory_db', 'sales_db', 'reviews_db', 'analytics_db', 'auth_db']
        for db in required_dbs:
            if db in databases:
                print(f"✅ {db} exists")
            else:
                print(f"❌ {db} is missing")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error checking databases: {e}")

if __name__ == "__main__":
    check_database_setup()