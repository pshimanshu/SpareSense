import requests
import random
import time
from dotenv import load_dotenv
import os

# Configuration
API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com"

def run_simulation():
    # --- BLOCK 1: FETCH MERCHANTS ---
    try:
        print("DEBUG: Attempting to fetch merchants...")
        merch_req = requests.get(f"{BASE_URL}/merchants?key={API_KEY}", timeout=10)
        merch_req.raise_for_status()
        merchants = merch_req.json()
        print("SUCCESS: Merchants loaded.")
    except Exception as e:
        print(f"ERROR IN BLOCK 1 (Merchants): Could not connect to API. Details: {e}")
        return

    # --- BLOCK 2: FETCH CUSTOMERS ---
    try:
        print("DEBUG: Attempting to fetch customers...")
        cust_req = requests.get(f"{BASE_URL}/customers?key={API_KEY}", timeout=10)
        cust_req.raise_for_status()
        customers = cust_req.json()
        print(f"SUCCESS: {len(customers)} Customers loaded.")
    except Exception as e:
        print(f"ERROR IN BLOCK 2 (Customers): Failed to retrieve customer list. Details: {e}")
        return

    # --- BLOCK 3: PROCESS EACH CUSTOMER ---
    for customer in customers:
        c_id = customer['_id']
        name = f"{customer['first_name']} {customer['last_name']}"
        
        try:
            # Fetch Account for this customer
            acc_req = requests.get(f"{BASE_URL}/customers/{c_id}/accounts?key={API_KEY}", timeout=5)
            acc_req.raise_for_status()
            accounts = acc_req.json()
            
            if not accounts:
                print(f"SKIP: No account found for {name}")
                continue
                
            acc_id = accounts[0]['_id']
        except Exception as e:
            print(f"ERROR IN BLOCK 3 (Account Fetch): Failed for customer {name}. Details: {e}")
            continue

        # Persona Logic
        persona = random.choice(['High Spender', 'Essentialist', 'Reckless'])
        if persona == 'High Spender':
            items = [("Luxury Goods", 100, 300), ("Fine Dining", 100, 200)]
            count = 2
        elif persona == 'Essentialist':
            items = [("Groceries", 30, 80)]
            count = 1
        else:
            items = [("Coffee", 5, 12), ("Fast Food", 12, 25)]
            count = 4

        print(f"\nSTARTING: {name} ({persona})")

        # --- BLOCK 4: CREATE PURCHASES ---
        for i in range(count):
            label, min_p, max_p = random.choice(items)
            merchant = random.choice(merchants)
            amt = random.randint(min_p, max_p)

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
                    print(f"  [Txn {i+1}] Success: Spent ${amt} at {merchant['name']}")
                else:
                    print(f"  [Txn {i+1}] API Rejected: {res.status_code} - {res.text}")
            except Exception as e:
                print(f"  [Txn {i+1}] ERROR IN BLOCK 4 (Purchase Post): Details: {e}")
            
            time.sleep(0.1)

if __name__ == "__main__":
    run_simulation()


# STARTING: Sai Puneeth Bonagiri (High Spender)
#   [Txn 1] Success: Spent $132 at The Brow House
#   [Txn 2] Success: Spent $119 at Chik-Fil-A

# STARTING: Harper Davis (High Spender)
#   [Txn 1] Success: Spent $246 at Fresh Farms
#   [Txn 2] Success: Spent $217 at Discount Tire Store - College Station, TX

# STARTING: Olivia Johnson (Reckless)
#   [Txn 1] Success: Spent $10 at Champion Firearms Corporation
#   [Txn 2] Success: Spent $23 at Airbnb
#   [Txn 3] Success: Spent $20 at Shell Consulting
#   [Txn 4] Success: Spent $9 at Merchant3

# STARTING: Sebastian Martinez (High Spender)
#   [Txn 1] Success: Spent $179 at Holt Ltd
#   [Txn 2] Success: Spent $157 at Merchant9

# STARTING: Ethan Smith (Essentialist)
#   [Txn 1] Success: Spent $50 at CVS Caremark

# STARTING: Emma Gonzalez (High Spender)
#   [Txn 1] Success: Spent $105 at TicketMaster
#   [Txn 2] Success: Spent $154 at Shell

# STARTING: Aria Thomas (High Spender)
#   [Txn 1] Success: Spent $104 at Amazon
#   [Txn 2] Success: Spent $147 at Merchant14

# STARTING: Zoe Wilson (Essentialist)
#   [Txn 1] Success: Spent $73 at OpenAI

# STARTING: Mateo Moore (Reckless)
#   [Txn 1] Success: Spent $11 at Gap
#   [Txn 2] Success: Spent $15 at Nike
#   [Txn 3] Success: Spent $14 at Delta Airlines
#   [Txn 4] Success: Spent $18 at DENNY'S

# STARTING: Chloe Jones (Reckless)
#   [Txn 1] Success: Spent $12 at Merchant5
#   [Txn 2] Success: Spent $7 at Merchant4
#   [Txn 3] Success: Spent $7 at Whole Foods
#   [Txn 4] Success: Spent $6 at Walgreens

# STARTING: Liam Brown (Essentialist)
#   [Txn 1] Success: Spent $60 at Wendys

# STARTING: Daniel Jackson (High Spender)
#   [Txn 1] Success: Spent $187 at Merchant10
#   [Txn 2] Success: Spent $177 at Caffè Amouri

# STARTING: Layla Lopez (High Spender)
#   [Txn 1] Success: Spent $177 at Amazon
#   [Txn 2] Success: Spent $118 at Con Edison

# STARTING: Isabella Garcia (Reckless)
#   [Txn 1] Success: Spent $12 at Rogers-Smith
#   [Txn 2] Success: Spent $18 at Panera Bread
#   [Txn 3] Success: Spent $9 at Merchant1
#   [Txn 4] Success: Spent $9 at GROUPBUY

# STARTING: Mia Williams (Reckless)
#   [Txn 1] Success: Spent $20 at Georgia Tech
#   [Txn 2] Success: Spent $21 at Capitol City Brewing Company
#   [Txn 3] Success: Spent $13 at NTB - National Tire & Battery
#   [Txn 4] Success: Spent $13 at Coursera

# STARTING: Noah Rodriguez (Reckless)
#   [Txn 1] Success: Spent $25 at Mercer, Young and Smith
#   [Txn 2] Success: Spent $11 at Walgreens
#   [Txn 3] Success: Spent $9 at Tap Room
#   [Txn 4] Success: Spent $9 at Christopher's World Grille

# STARTING: James Miller (Reckless)
#   [Txn 1] Success: Spent $25 at Airbnb
#   [Txn 2] Success: Spent $13 at Joes
#   [Txn 3] Success: Spent $17 at zpizza
#   [Txn 4] Success: Spent $9 at Hale, Myers and Larson Event Planning

# STARTING: Julian Taylor (Essentialist)
#   [Txn 1] Success: Spent $73 at Pauly Honda

# STARTING: Lucas Martin (Essentialist)
#   [Txn 1] Success: Spent $56 at Ramsey, Hansen and Mendoza Tech Store

# STARTING: Sophia Anderson (High Spender)
#   [Txn 1] Success: Spent $292 at Trader Joe's
#   [Txn 2] Success: Spent $141 at REI

# STARTING: Alexander Hernandez (Reckless)
#   [Txn 1] Success: Spent $7 at CalHacks
#   [Txn 2] Success: Spent $9 at Trader Joes
#   [Txn 3] Success: Spent $12 at Hilton
#   [Txn 4] Success: Spent $9 at Joes