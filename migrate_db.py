"""
Migration script to add new columns to support_tickets table.
Run this after updating models.py.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'buildup.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(support_tickets)")
    columns = {col[1] for col in cursor.fetchall()}
    
    if 'name' not in columns:
        cursor.execute("ALTER TABLE support_tickets ADD COLUMN name VARCHAR(100)")
        print("Added 'name' column")
    
    if 'email' not in columns:
        cursor.execute("ALTER TABLE support_tickets ADD COLUMN email VARCHAR(120)")
        print("Added 'email' column")
    
    if 'resolved_at' not in columns:
        cursor.execute("ALTER TABLE support_tickets ADD COLUMN resolved_at DATETIME")
        print("Added 'resolved_at' column")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()

