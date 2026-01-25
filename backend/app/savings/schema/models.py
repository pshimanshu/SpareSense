from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class CreateWalletRequest(BaseModel):
    user_id: str

class TransferRequest(BaseModel):
    user_id: str
    amount_sol: float

class WalletResponse(BaseModel):
    user_id: str
    wallet_address: str
    created_at: datetime

class TransferResponse(BaseModel):
    success: bool
    transaction_signature: Optional[str] = None
    amount_sol: Optional[float] = None
    to_wallet: Optional[str] = None
    error: Optional[str] = None

class BalanceResponse(BaseModel):
    wallet_address: str
    balance_sol: float