import requests
import random
import time
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com"

def setup_accounts():
    # 1. Fetch all customers assigned to this API Key
    print("Fetching customers...")
    try:
        customers_res = requests.get(f"{BASE_URL}/customers?key={API_KEY}")
        customers_res.raise_for_status()
        customers = customers_res.json()
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return

    print(f"Found {len(customers)} customers. Creating checking accounts...\n")

    # 2. Iterate through customers and create accounts
    for i, customer in enumerate(customers, 1):
        c_id = customer['_id']
        name = f"{customer['first_name']} {customer['last_name']}"
        
        # Account payload (account_number removed)
        payload = {
            "type": "Checking",
            "nickname": f"{customer['first_name']}'s Checking",
            "rewards": 0,
            "balance": random.randint(0, 1000)
        }

        # POST to /customers/{id}/accounts
        account_url = f"{BASE_URL}/customers/{c_id}/accounts?key={API_KEY}"
        
        try:
            response = requests.post(account_url, json=payload)
            
            if response.status_code == 201:
                print(f"[{i}] Success: {name} | Balance: ${payload['balance']}")
            else:
                print(f"[{i}] Failed for {name}: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"[{i}] Connection Error for {name}: {e}")

        # Small delay to keep the API happy
        time.sleep(0.1)

if __name__ == "__main__":
    setup_accounts()