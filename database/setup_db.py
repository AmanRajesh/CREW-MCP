import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'hospital_inventory.db')

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        part_number TEXT PRIMARY KEY,
        stock_level INTEGER,
        unit_cost REAL
    )
    ''')
    
    # Insert mock data
    mock_data = [
        ('404B', 5, 120.00),      # Standard part
        ('SPO2-AMB', 2, 650.00),  # High cost part > $500 threshold
        ('MRI-MAG-01', 0, 12000.00) # Out of stock, extreme cost
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO inventory (part_number, stock_level, unit_cost) 
    VALUES (?, ?, ?)
    ''', mock_data)
    
    conn.commit()
    conn.close()
    print(f"Database setup complete at {DB_PATH}")

if __name__ == "__main__":
    setup_db()
