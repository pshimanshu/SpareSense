from fastapi import FastAPI, HTTPException
from .savings.solana_service import SolanaService
from .savings.schema.models import (
    CreateWalletRequest,
    WalletResponse,
    TransferRequest,
    TransferResponse,
    BalanceResponse,
)
app = FastAPI(title="FinWise API")

# Initialize Solana service
solana_service = SolanaService()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/wallets", response_model=WalletResponse)
def create_user_wallet(request: CreateWalletRequest):
    """Create a new Solana wallet for a user"""
    try:
        # Check if wallet already exists for this user
        existing_wallet = solana_service.get_user_wallet(request.user_id)
        if existing_wallet:
            raise HTTPException(status_code=409, detail=f"Wallet already exists for user {request.user_id}")
        
        wallet_info = solana_service.create_user_wallet(request.user_id)
        return WalletResponse(**wallet_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create wallet: {str(e)}")

@app.get("/wallets/{user_id}", response_model=WalletResponse)
def get_user_wallet(user_id: str):
    """Get user's wallet information"""
    wallet_info = solana_service.get_user_wallet(user_id)
    if not wallet_info:
        raise HTTPException(status_code=404, detail="Wallet not found for user")
    return WalletResponse(**wallet_info)

@app.post("/transfer", response_model=TransferResponse)
def transfer_sol_to_user(request: TransferRequest):
    """Transfer SOL from bank's wallet to user's wallet"""
    # First, get the user's wallet
    wallet_info = solana_service.get_user_wallet(request.user_id)
    if not wallet_info:
        raise HTTPException(status_code=404, detail="Wallet not found for user")

    # Transfer SOL
    result = solana_service.transfer_sol(wallet_info["wallet_address"], request.amount_sol)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Transfer failed"))

    return TransferResponse(**result)


@app.get("/wallets/main/balance", response_model=BalanceResponse)
def get_main_wallet_balance():
    """Get the balance of the main wallet"""
    balance = solana_service.get_main_wallet_balance()
    return BalanceResponse(
        wallet_address="main_wallet",
        balance_sol=balance
    )


@app.get("/wallets/{user_id}/balance", response_model=BalanceResponse)
def get_user_wallet_balance(user_id: str):
    """Get the SOL balance of a user's wallet"""
    wallet_info = solana_service.get_user_wallet(user_id)
    if not wallet_info:
        raise HTTPException(status_code=404, detail="Wallet not found for user")

    balance = solana_service.get_wallet_balance(wallet_info["wallet_address"])
    return BalanceResponse(
        wallet_address=wallet_info["wallet_address"],
        balance_sol=balance
    )