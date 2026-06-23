import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ArogyaConnect Doctor Directory")

# Mock database of hospitals and doctors located in Bengaluru
DATABASE = {
    "General Medicine": [
        {
            "name": "Dr. Priya Desai",
            "hospital": "Lakeside Care Hospital",
            "location": "Bengaluru",
            "slots": ["10:00 AM - 12:00 PM", "02:00 PM - 04:00 PM"]
        }
    ],
    "Cardiology": [
        {
            "name": "Dr. Aarav Sharma",
            "hospital": "Skyline Multi-Specialty",
            "location": "Bengaluru",
            "slots": ["09:00 AM - 11:00 AM", "03:00 PM - 05:00 PM"]
        }
    ],
    "Pediatrics": [
        {
            "name": "Dr. Rohan Gupta",
            "hospital": "Lakeside Care Hospital",
            "location": "Bengaluru",
            "slots": ["11:00 AM - 01:00 PM"]
        }
    ],
    "Dermatology": [
        {
            "name": "Dr. Sunita Rao",
            "hospital": "Skyline Multi-Specialty",
            "location": "Bengaluru",
            "slots": ["04:00 PM - 06:00 PM"]
        }
    ],
    "Orthopedics": [
        {
            "name": "Dr. Rohan Iyer",
            "hospital": "Lakeside Care Hospital",
            "location": "Bengaluru",
            "slots": ["02:00 PM - 05:00 PM"]
        }
    ],
    "Neurology": [
        {
            "name": "Dr. Vikram Shah",
            "hospital": "Skyline Multi-Specialty",
            "location": "Bengaluru",
            "slots": ["10:00 AM - 01:00 PM"]
        }
    ]
}

@mcp.tool()
def get_doctors_by_specialty(specialty: str) -> str:
    """Get list of doctors, hospitals, and available time slots in Bengaluru for a given medical specialty.
    
    Args:
        specialty: The medical specialty to search for (e.g., 'General Medicine', 'Cardiology', 'Pediatrics', 'Dermatology').
    """
    specialty_lower = specialty.lower().strip()
    
    matched_key = None
    for key in DATABASE.keys():
        if key.lower() in specialty_lower or specialty_lower in key.lower():
            matched_key = key
            break
            
    if not matched_key:
        matched_key = "General Medicine"
        
    doctors = DATABASE[matched_key]
    return json.dumps({
        "specialty": matched_key,
        "doctors": doctors
    }, indent=2)

if __name__ == "__main__":
    mcp.run()
