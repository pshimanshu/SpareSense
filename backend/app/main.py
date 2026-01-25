from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from fastapi.responses import HTMLResponse
import requests
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv 
import os

app = FastAPI(title="FinWise API")

# Replace with your actual API key from your Nessie profile
load_dotenv()
NESSIE_API_KEY = os.getenv("NESSIE_API_KEY")
BASE_URL = "http://api.nessieisreal.com"

@app.get("/")
def root():
    return {"status": "good"}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Integrated Account Endpoints ---

@app.get("/accounts")
async def get_all_accounts():
    """Calls Nessie to fetch all accounts."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/accounts?key={NESSIE_API_KEY}")
        return response.json()

@app.get("/accounts/{account_id}")
async def get_account(account_id: str):
    """Calls Nessie to fetch account details by ID."""
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/accounts/{account_id}?key={NESSIE_API_KEY}"
        response = await client.get(url)
        return response.json()

@app.get("/customers/{customer_id}/accounts")
async def get_accounts_by_customer(customer_id: str):
    """Calls Nessie to fetch all accounts belonging to a specific customer."""
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/customers/{customer_id}/accounts?key={NESSIE_API_KEY}"
        response = await client.get(url)
        return response.json()

# Model based on Nessie Schema
class AccountCreate(BaseModel):
    type: str  # Options: 'Credit Card', 'Savings', 'Checking'
    nickname: str
    rewards: int = 0
    balance: int = 0
    account_number: Optional[str] = None # 16 digit number

@app.post("/customers/{customer_id}/accounts", status_code=201)
async def create_customer_account(customer_id: str, account: AccountCreate):
    """
    Creates an account for the customer with the specified id.
    """
    url = f"{BASE_URL}/customers/{customer_id}/accounts?key={NESSIE_API_KEY}"
    
    async with httpx.AsyncClient() as client:
        # Nessie expects application/json content type
        response = await client.post(
            url, 
            json=account.dict(exclude_unset=True)
        )
        
        if response.status_code == 201:
            return {
                "code": 201,
                "message": "Account created",
                "objectCreated": response.json()
            }
        
        # Handle errors (e.g., 404 if customer_id doesn't exist)
        raise HTTPException(
            status_code=response.status_code, 
            detail=response.json().get("message", "Error creating account")
        )

# --- Schema Models ---
class Address(BaseModel):
    street_number: str
    street_name: str
    city: str
    state: str
    zip: str

class Customer(BaseModel):
    first_name: str
    last_name: str
    address: Address

# --- CUSTOMER ENDPOINTS ---

@app.get("/accounts/{account_id}/customer", tags=["Customers"])
async def get_customer_by_account(account_id: str):
    """Get the customer that owns the specified account."""
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/accounts/{account_id}/customer?key={NESSIE_API_KEY}"
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Customer not found for this account")
        return response.json()

@app.get("/customers", tags=["Customers"])
async def get_all_customers():
    """Get all customers."""
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/customers?key={NESSIE_API_KEY}"
        response = await client.get(url)
        return response.json()

@app.get("/customers/{id}", tags=["Customers"])
async def get_customer_by_id(id: str):
    """Get customer by id."""
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/customers/{id}?key={NESSIE_API_KEY}"
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Customer not found")
        return response.json()

@app.post("/customers", status_code=201, tags=["Customers"])
async def create_customer(customer: Customer):
    """Create a new customer."""
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/customers?key={NESSIE_API_KEY}"
        response = await client.post(url, json=customer.dict())
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail="Failed to create customer")
        return response.json()

@app.get("/view-purchases", response_class=HTMLResponse)
async def view_purchases_html():
    try:
        # 1. Get all customers
        customers = requests.get(f"{BASE_URL}/customers?key={NESSIE_API_KEY}").json()
        
        table_rows = ""
        
        for customer in customers:
            c_id = customer['_id']
            name = f"{customer['first_name']} {customer['last_name']}"
            
            # 2. Get accounts for this customer
            accounts = requests.get(f"{BASE_URL}/customers/{c_id}/accounts?key={NESSIE_API_KEY}").json()
            
            for account in accounts:
                acc_id = account['_id']
                
                # 3. Get purchases for this account
                purchases = requests.get(f"{BASE_URL}/accounts/{acc_id}/purchases?key={NESSIE_API_KEY}").json()
                
                for p in purchases:
                    # Building the HTML table row
                    table_rows += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{account['type']}</td>
                        <td>{p.get('description', 'N/A')}</td>
                        <td>${p['amount']}</td>
                        <td>{p['purchase_date']}</td>
                        <td><span class="status-tag">{p['status']}</span></td>
                    </tr>
                    """
        
        # 4. Final HTML Structure with some basic CSS styling
        html_content = f"""
        <html>
            <head>
                <title>Purchase History</title>
                <style>
                    body {{ font-family: sans-serif; margin: 40px; background-color: #f4f7f6; }}
                    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #007bff; color: white; text-transform: uppercase; font-size: 14px; }}
                    tr:hover {{ background-color: #f1f1f1; }}
                    .status-tag {{ background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
                </style>
            </head>
            <body>
                <h2>All Customer Purchases</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Customer Name</th>
                            <th>Account Type</th>
                            <th>Description</th>
                            <th>Amount</th>
                            <th>Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows if table_rows else "<tr><td colspan='6'>No purchases found.</td></tr>"}
                    </tbody>
                </table>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

@app.get("/customers-dashboard", response_class=HTMLResponse)
async def get_interactive_dashboard():
    try:
        # 1. Fetch Customers
        customers = requests.get(f"{BASE_URL}/customers?key={NESSIE_API_KEY}").json()
        
        # 2. Fetch Merchants (to map names)
        merch_data = requests.get(f"{BASE_URL}/merchants?key={NESSIE_API_KEY}").json()
        merchants = {m['_id']: m['name'] for m in merch_data}

        accordion_html = ""

        for cust in customers:
            c_id = cust['_id']
            full_name = f"{cust['first_name']} {cust['last_name']}"
            
            # Fetch Accounts and then Purchases
            acc_res = requests.get(f"{BASE_URL}/customers/{c_id}/accounts?key={NESSIE_API_KEY}").json()
            all_purchases = []
            if acc_res:
                for acc in acc_res:
                    p_res = requests.get(f"{BASE_URL}/accounts/{acc['_id']}/purchases?key={NESSIE_API_KEY}").json()
                    all_purchases.extend(p_res)

            # Build the Purchase Rows for this specific customer
            purchase_rows = ""
            for p in all_purchases:
                m_name = merchants.get(p.get('merchant_id'), "Unknown")
                purchase_rows += f"""
                    <tr>
                        <td>{p['purchase_date']}</td>
                        <td>{m_name}</td>
                        <td>{p.get('description', 'N/A')}</td>
                        <td><strong>${p['amount']}</strong></td>
                    </tr>
                """

            # Wrap in an expandable section
            accordion_html += f"""
            <div class="customer-section">
                <button class="accordion" onclick="toggleAccordion(this)">
                    {full_name} <span class="count">({len(all_purchases)} Transactions)</span>
                </button>
                <div class="panel">
                    <table>
                        <thead>
                            <tr><th>Date</th><th>Merchant</th><th>Item</th><th>Amount</th></tr>
                        </thead>
                        <tbody>
                            {purchase_rows if purchase_rows else "<tr><td colspan='4'>No data</td></tr>"}
                        </tbody>
                    </table>
                </div>
            </div>
            """

        full_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; padding: 30px; background: #f0f2f5; }}
                .accordion {{ background-color: #fff; color: #444; cursor: pointer; padding: 18px; width: 100%; text-align: left; border: 1px solid #ddd; border-radius: 5px; outline: none; font-size: 16px; transition: 0.3s; margin-top: 5px; display: flex; justify-content: space-between; }}
                .accordion:hover {{ background-color: #e7f3ff; border-color: #007bff; }}
                .panel {{ padding: 0 18px; display: none; background-color: white; overflow: hidden; border: 1px solid #ddd; border-top: none; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background: #f8f9fa; color: #666; text-align: left; padding: 10px; border-bottom: 2px solid #eee; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                .count {{ color: #007bff; font-weight: bold; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>Banking Customer Portal</h1>
            {accordion_html}
            <script>
                function toggleAccordion(btn) {{
                    btn.classList.toggle("active");
                    var panel = btn.nextElementSibling;
                    panel.style.display = (panel.style.display === "block") ? "none" : "block";
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=full_html)
    except Exception as e:
        return HTMLResponse(content=f"Error: {e}", status_code=500)

@app.get("/transactions-by-customer")
async def get_customers_with_transactions(name: Optional[str] = Query(None, description="Filter by customer name")):
    try:
        # 1. Fetch Merchants (for mapping)
        merch_data = requests.get(f"{BASE_URL}/merchants?key={NESSIE_API_KEY}").json()
        merchants = {m['_id']: m['name'] for m in merch_data}

        # 2. Fetch Customers
        customers = requests.get(f"{BASE_URL}/customers?key={NESSIE_API_KEY}").json()
        
        final_list = []

        for cust in customers:
            full_name = f"{cust['first_name']} {cust['last_name']}"
            
            # --- FILTER LOGIC ---
            # If a name query is provided, skip customers that don't match
            if name and name.lower() not in full_name.lower():
                continue

            c_id = cust['_id']
            
            # Fetch Accounts and Purchases
            acc_res = requests.get(f"{BASE_URL}/customers/{c_id}/accounts?key={NESSIE_API_KEY}").json()
            
            customer_purchases = []
            if acc_res:
                for acc in acc_res:
                    p_res = requests.get(f"{BASE_URL}/accounts/{acc['_id']}/purchases?key={NESSIE_API_KEY}").json()
                    for p in p_res:
                        customer_purchases.append({
                            "purchase_id": p.get("_id"),
                            "merchant_name": merchants.get(p.get('merchant_id'), "Unknown"),
                            "description": p.get('description'),
                            "amount": p.get('amount'),
                            "date": p.get('purchase_date'),
                        })

            final_list.append({
                "name": full_name,
                "customer_id": c_id,
                "transaction_count": len(customer_purchases),
                "transactions": customer_purchases
            })

        return final_list

    except Exception as e:
        return {"error": str(e)}