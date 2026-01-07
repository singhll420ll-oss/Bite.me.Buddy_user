# init_db.py - Optional helper script
import os
import psycopg

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
        conn = psycopg.connect(database_url)
        cur = conn.cursor()
        
        # Read schema.sql if exists, else use hardcoded schema
        if os.path.exists('schema.sql'):
            with open('schema.sql', 'r') as f:
                sql_commands = f.read()
            cur.execute(sql_commands)
        else:
            # Create tables directly
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    profile_pic VARCHAR(255),
                    full_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(15) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    location TEXT NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Users table created")
        
        conn.commit()
        
        # Verify tables
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cur.fetchall()
        print("📊 Available tables:", [table[0] for table in tables])
        
        cur.close()
        conn.close()
        
        print("✅ Database initialization completed")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

if __name__ == '__main__':
    init_database()