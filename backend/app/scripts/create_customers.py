import requests
import random
import time
from dotenv import load_dotenv
import os

# Configuration
API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = f"http://api.nessieisreal.com/customers?key={API_KEY}"

# Diverse Name Pools
FIRST_NAMES = [
    "Liam", "Emma", "Noah", "Olivia", "James", "Sophia", "Lucas", "Mia", 
    "Ethan", "Isabella", "Mateo", "Aria", "Sebastian", "Zoe", "Alexander", 
    "Layla", "Julian", "Chloe", "Daniel", "Harper"
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", 
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", 
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
]
STREETS = ["Oak St", "Pine Rd", "Maple Ave", "Cedar Blvd", "Washington St", "Lakeview Dr"]

def create_diverse_customers(count):
    # Ensure we don't exceed our name list or just shuffle them
    random.shuffle(FIRST_NAMES)
    random.shuffle(LAST_NAMES)

    for i in range(count):
        # Pick names based on index to ensure variety
        f_name = FIRST_NAMES[i % len(FIRST_NAMES)]
        l_name = LAST_NAMES[i % len(LAST_NAMES)]
        
        payload = {
            "first_name": f_name,
            "last_name": l_name,
            "address": {
                "street_number": str(random.randint(10, 999)),
                "street_name": random.choice(STREETS),
                "city": "Gainesville",
                "state": "FL",
                "zip": "32608"
            }
        }

        try:
            # The 'json' parameter automatically handles Content-Type: application/json
            response = requests.post(BASE_URL, json=payload)
            
            if response.status_code == 201:
                print(f"[{i+1}] Success: Created {f_name} {l_name}")
            else:
                print(f"[{i+1}] Failed: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"[{i+1}] Connection Error: {e}")

        # Short pause to prevent rate limiting
        time.sleep(0.2)

if __name__ == "__main__":
    create_diverse_customers(20)