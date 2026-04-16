from fastmcp import FastMCP
import sqlite3
import os

mcp = FastMCP("PhilipsDataServer")

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'hospital_inventory.db')
MANUAL_PATH = os.path.join(BASE_DIR, 'manual.txt')
@mcp.tool()
def search_technical_manual(symptom_or_error: str) -> str:
    """Searches the unstructured technical manual for the given symptom or error code and returns the SKU and required safety precautions."""
    if not os.path.exists(MANUAL_PATH):
        return "Error: manual.txt not found."
    
    with open(MANUAL_PATH, 'r') as f:
        manual_content = f.read()
        
    lines = manual_content.split('\n')
    relevant_lines = []
    
    symptom_lower = symptom_or_error.lower()
    in_section = False
    
    for line in lines:
        if symptom_lower in line.lower() or (in_section and line.startswith("Part Number (SKU):")):
            in_section = True
            relevant_lines.append(line)
        elif in_section:
            if line.strip() == "" or line.startswith("---"):
                break
            relevant_lines.append(line)
            
    if not relevant_lines:
        return f"No match found for '{symptom_or_error}' in the manual."
        
    return "\n".join(relevant_lines)

@mcp.tool()
def check_hospital_inventory(part_number: str) -> str:
    """Checks the hospital inventory database for stock levels and unit cost for a given part number."""
    if not os.path.exists(DB_PATH):
        return "Error: Database not found."
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT stock_level, unit_cost FROM inventory WHERE part_number=?", (part_number,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return f"Part {part_number}: {result[0]} in stock, Unit Cost: ${result[1]:.2f}"
        else:
            return f"Part {part_number} not found in inventory."
    except Exception as e:
        return f"Database error: {str(e)}"

if __name__ == "__main__":
    mcp.run()