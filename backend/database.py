"""
Database models and utilities.
"""
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class Database:
    def __init__(self):
        self.conn = None
        self.database_url = os.getenv('DATABASE_URL')
    
    def connect(self):
        """Connect to the database"""
        try:
            self.conn = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
            print("Database connected")
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def init_tables(self):
        """Initialize database tables"""
        if not self.conn:
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # Create devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    ip VARCHAR(45) NOT NULL,
                    mac VARCHAR(17) NOT NULL,
                    status VARCHAR(20) DEFAULT 'offline',
                    uptime FLOAT DEFAULT 0,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    device_id INTEGER REFERENCES devices(id),
                    severity VARCHAR(20) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Create uptime_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uptime_history (
                    id SERIAL PRIMARY KEY,
                    device_id INTEGER REFERENCES devices(id),
                    uptime_percentage FLOAT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            cursor.close()
            print("Database tables initialized")
            return True
        except Exception as e:
            print(f"Error initializing tables: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
