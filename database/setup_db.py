import sqlite3
import os

# Use absolute path to ensure it hits the correct file regardless of where you run it
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'hospital_inventory.db')

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        part_number TEXT PRIMARY KEY,
        stock_level INTEGER,
        unit_cost REAL
    )
    ''')
    
    # Use REPLACE so that existing SKUs get updated
    mock_data = [
        ('404B', 5, 650.00),      # Updated to $650
        ('SPO2-AMB', 2, 650.00),
        ('MRI-MAG-01', 0, 12000.00)
    ]
    
    cursor.executemany('''
    INSERT OR REPLACE INTO inventory (part_number, stock_level, unit_cost) 
    VALUES (?, ?, ?)
    ''', mock_data)
    
    # CRITICAL: Changes are only saved to disk after commit()
    conn.commit() 
    conn.close()
    print(f"Database successfully updated at {DB_PATH}")

if __name__ == "__main__":
    setup_db()