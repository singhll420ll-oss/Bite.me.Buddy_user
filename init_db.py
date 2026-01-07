# init_db.py - Optional file if you want to initialize database manually
import os
import psycopg2

def init_database():
    """Initialize database by creating tables"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not set in environment")
        return
    
    # Fix for Render PostgreSQL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Read schema.sql
        with open('schema.sql', 'r') as f:
            sql_commands = f.read()
        
        # Execute SQL commands
        cur.execute(sql_commands)
        conn.commit()
        
        print("✅ Database tables created successfully")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

if __name__ == '__main__':
    init_database()