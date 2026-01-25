import os
import json
import requests
import time
from dotenv import load_dotenv

# 1. Load configuration
load_dotenv()
API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com"

def delete_all_purchases():
    filename = "purchase_ids.json"

    # Check if the file exists
    if not os.path.exists(filename):
        print(f"Error: {filename} not found. Run the extraction script first.")
        return

    # Load IDs from the file
    with open(filename, "r") as f:
        purchase_ids = json.load(f)

    if not purchase_ids:
        print("No IDs found in the file to delete.")
        return

    print(f"Found {len(purchase_ids)} transactions to delete. Starting cleanup...")

    success_count = 0
    fail_count = 0

    for p_id in purchase_ids:
        # Nessie delete endpoint for purchases
        url = f"{BASE_URL}/purchases/{p_id}?key={API_KEY}"
        
        try:
            response = requests.delete(url)
            
            # 204 No Content is the standard success code for DELETE
            if response.status_code in [200, 204]:
                print(f"SUCCESS: Deleted {p_id}")
                success_count += 1
            else:
                print(f"FAILED: Could not delete {p_id}. Status: {response.status_code}")
                fail_count += 1
        
        except Exception as e:
            print(f"ERROR: Connection error for {p_id}: {e}")
            fail_count += 1

        # Small sleep to respect rate limits
        time.sleep(0.1)

    print("\n--- Cleanup Summary ---")
    print(f"Total Attempted: {len(purchase_ids)}")
    print(f"Successfully Deleted: {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    delete_all_purchases()