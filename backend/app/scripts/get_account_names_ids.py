import os
import asyncio
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com"

async def get_customer_accounts(client, customer):
    """Fetch all account IDs for a single customer."""
    c_id = customer['_id']
    name = f"{customer['first_name']} {customer['last_name']}"
    
    url = f"{BASE_URL}/customers/{c_id}/accounts?key={API_KEY}"
    
    try:
        resp = await client.get(url)
        # Handle cases where the response might not be JSON
        accounts = resp.json()
        
        # Extract only the IDs from the account objects
        account_ids = [acc['_id'] for acc in accounts]
        
        return {
            "name": name,
            "customer_id": c_id,
            "account_ids": account_ids
        }
    except Exception as e:
        return {"name": name, "customer_id": c_id, "error": str(e)}

async def main():
    async with httpx.AsyncClient() as client:
        print("Connecting to Nessie API...")
        
        # 1. Get all customers
        try:
            cust_resp = await client.get(f"{BASE_URL}/customers?key={API_KEY}")
            cust_resp.raise_for_status()
            customers = cust_resp.json()
        except Exception as e:
            print(f"Failed to fetch customers: {e}")
            return

        # 2. Fetch account IDs in parallel
        print(f"Mapping accounts for {len(customers)} customers...")
        tasks = [get_customer_accounts(client, c) for c in customers]
        results = await asyncio.gather(*tasks)

        # 3. Save to JSON file
        filename = "customer_account_map.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)
        
        print(f"\nSUCCESS: Data saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main())