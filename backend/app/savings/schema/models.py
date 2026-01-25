from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class CreateWalletRequest(BaseModel):
    user_id: str

class TransferRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$', description="Unique user identifier, alphanumeric with hyphens and underscores only")
    amount_sol: float = Field(gt=0, description="Amount in SOL to transfer")

class WalletResponse(BaseModel):
    user_id: str = Field(min_length=1, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$', description="Unique user identifier, alphanumeric with hyphens and underscores only")
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