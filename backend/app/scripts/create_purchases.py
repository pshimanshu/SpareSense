import requests
import random
import time
from dotenv import load_dotenv
import os

# Configuration
load_dotenv()
API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com" # Using the alternative stable URL

def run_simulation():
    # --- BLOCK 1: FETCH MERCHANTS ---
    try:
        print("DEBUG: Attempting to fetch merchants...")
        merch_req = requests.get(f"{BASE_URL}/merchants?key={API_KEY}", timeout=10)
        merch_req.raise_for_status()
        merchants = merch_req.json()
        print("SUCCESS: Merchants loaded.")
    except Exception as e:
        print(f"ERROR IN BLOCK 1 (Merchants): {e}")
        return

    # --- BLOCK 2: FETCH CUSTOMERS ---
    try:
        cust_req = requests.get(f"{BASE_URL}/customers?key={API_KEY}", timeout=10)
        cust_req.raise_for_status()
        customers = cust_req.json()
        print(f"SUCCESS: Found {len(customers)} customers.")
    except Exception as e:
        print(f"ERROR IN BLOCK 2 (Customers): {e}")
        return

    # --- BLOCK 3: PROCESS EACH CUSTOMER ---
    for customer in customers:
        c_id = customer['_id']
        name = f"{customer['first_name']} {customer['last_name']}"
        
        try:
            acc_req = requests.get(f"{BASE_URL}/customers/{c_id}/accounts?key={API_KEY}", timeout=5)
            acc_req.raise_for_status()
            accounts = acc_req.json()
            
            if not accounts:
                print(f"SKIP: No account for {name}")
                continue
                
            acc_id = accounts[0]['_id']
        except Exception as e:
            print(f"ERROR IN BLOCK 3: {e}")
            continue

        # Persona Logic (Determines price range and items)
        persona = random.choice(['High Spender', 'Essentialist', 'Reckless'])
        
        if persona == 'High Spender':
            items = [("Luxury Goods", 100.00, 300.00), ("Fine Dining", 80.00, 200.00)]
        elif persona == 'Essentialist':
            items = [("Groceries", 20.00, 95.00), ("Pharmacy", 10.00, 50.00)]
        else: # Reckless
            items = [("Coffee", 3.50, 9.75), ("Fast Food", 8.25, 22.40), ("Entertainment", 15.00, 45.00)]

        print(f"\nSTARTING: {name} ({persona}) - Creating transactions...")

        # --- BLOCK 4: CREATE 25 PURCHASES ---
        for i in range(random.randint(2, 15)):
            label, min_p, max_p = random.choice(items)
            merchant = random.choice(merchants)
            
            # Generate decimal amount
            amt = round(random.uniform(min_p, max_p), 2)

            payload = {
                "merchant_id": merchant['_id'],
                "medium": "balance",
                "purchase_date": "2026-01-24",
                "amount": amt,
                "status": "completed",
                "description": label
            }

            try:
                res = requests.post(f"{BASE_URL}/accounts/{acc_id}/purchases?key={API_KEY}", json=payload, timeout=5)
                if res.status_code == 201:
                    print(f"  [{i+1}] Success: ${amt:.2f} at {merchant['name']}")
                else:
                    print(f"  [{i+1}] Rejected: {res.status_code}")
            except Exception as e:
                print(f"  [{i+1}] ERROR: {e}")
            
            # Small sleep to keep API calls stable
            time.sleep(0.05)

if __name__ == "__main__":
    run_simulation()