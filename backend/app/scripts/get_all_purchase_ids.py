import os
import requests
import json
from dotenv import load_dotenv

# 1. Load configuration
load_dotenv()
API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com"

def export_purchase_ids():
    if not API_KEY:
        print("Error: NESSIE_API_KEY not found in .env file.")
        return

    all_ids = []
    
    try:
        print("Fetching data from Nessie...")
        # Step 1: Get customers
        customers = requests.get(f"{BASE_URL}/customers?key={API_KEY}").json()
        
        for customer in customers:
            # Step 2: Get accounts
            acc_res = requests.get(f"{BASE_URL}/customers/{customer['_id']}/accounts?key={API_KEY}")
            accounts = acc_res.json()
            
            for account in accounts:
                # Step 3: Get purchases
                purch_res = requests.get(f"{BASE_URL}/accounts/{account['_id']}/purchases?key={API_KEY}")
                purchases = purch_res.json()
                
                # Extract IDs
                for p in purchases:
                    if '_id' in p:
                        all_ids.append(p['_id'])

        # --- OUTPUT TO FILE ---
        filename = "purchase_ids.json"
        with open(filename, "w") as f:
            json.dump(all_ids, f, indent=4)
        
        print(f"Done! Successfully saved {len(all_ids)} IDs to {filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    export_purchase_ids()