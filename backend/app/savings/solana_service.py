import fcntl
import json
import logging
import os
from typing import Optional, Dict, Any
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer as solders_transfer, TransferParams as SoldersTransferParams
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from datetime import datetime
import re

class SolanaService:
    LAMPORTS_PER_SOL = 1_000_000_000

    def __init__(self):
        # Using Solana devnet for testing purposes
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        self.client = Client(self.rpc_url)

        # Load the main wallet keypair
        self.main_keypair = self._load_bank_keypair()

    def _load_bank_keypair(self) -> Keypair:
        """Load the main wallet keypair from wallet-keypair.json"""
        try:
            with open("../wallet-keypair.json", "r") as f:
                keypair_data = json.load(f)
                return Keypair.from_bytes(bytes(keypair_data))
        except Exception as e:
            raise Exception(f"Failed to load main wallet keypair: {e}")

    def create_user_wallet(self, user_id: str) -> Dict[str, Any]:
        """
        Create a new Solana wallet for a user.
        In production, you'd want to securely store and manage these keys.
        For demo purposes, we'll generate a new keypair each time.
        """
        # Generate a new keypair for the user
        user_keypair = Keypair()

        # Get the public key (wallet address)
        wallet_address = str(user_keypair.pubkey())

        # In a real application, you'd store the private key securely
        # For now, we'll return the wallet address and store a mapping
        wallet_info = {
            "user_id": user_id,
            "wallet_address": wallet_address,
            "created_at": datetime.now().isoformat()
        }

        # Save wallet mapping (in production, use a database)
        self._save_wallet_mapping(wallet_info)

        return wallet_info

    def _save_wallet_mapping(self, wallet_info: Dict[str, Any]):
        """Save wallet mapping to a JSON file (demo purposes)"""
        mapping_file = "./app/savings/data/user_wallets.json"

        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(mapping_file), exist_ok=True)

            # Use file locking to prevent race conditions
            with open(mapping_file, 'r+') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    mappings = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    mappings = {}
                mappings[wallet_info["user_id"]] = wallet_info
                f.seek(0)
                f.truncate()
                json.dump(mappings, f, indent=2)

        except Exception as e:
            logging.warning(f"Failed to save wallet mapping: {e}")


    def get_user_wallet(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's wallet information"""
        mapping_file = "./app/savings/data/user_wallets.json"

        try:
            if os.path.exists(mapping_file):
                with open(mapping_file, "r") as f:
                    mappings = json.load(f)
                    return mappings.get(user_id)
        except Exception as e:
            logging.warning(f"Failed to load wallet mapping: {e}")

        return None

    def transfer_sol(self, to_wallet_address: str, amount_sol: float) -> Dict[str, Any]:
        """
        Transfer SOL from the main wallet to a user's wallet
        """

        # Validate the wallet address format before attempting the transfer
        if not re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', to_wallet_address):
            return {
                "success": False,
                "error": "Invalid wallet address format. Please provide a valid Solana wallet address."
            }
        
        # Check main wallet balance before attempting transfer
        main_balance = self.get_main_wallet_balance()
        if main_balance < amount_sol:
            return {
                "success": False,
                "error": f"Insufficient funds in main wallet. Available: {main_balance} SOL, Required: {amount_sol} SOL"
            }


        try:
            # Convert SOL to lamports (1 SOL = 1,000,000,000 lamports)
            amount_lamports = int(amount_sol * self.LAMPORTS_PER_SOL)

            # Create transfer instruction
            transfer_ix = solders_transfer(
                SoldersTransferParams(
                    from_pubkey=self.main_keypair.pubkey(),
                    to_pubkey=Pubkey.from_string(to_wallet_address),
                    lamports=amount_lamports
                )
            )

            # Get recent blockhash
            recent_blockhash = self.client.get_latest_blockhash().value.blockhash

            # Create transaction message
            message = MessageV0.try_compile(
                payer=self.main_keypair.pubkey(),
                instructions=[transfer_ix],
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash,
            )

            # Create and sign transaction
            tx = VersionedTransaction(message, [self.main_keypair])

            # Send transaction
            result = self.client.send_transaction(tx)

            if result.value:
                return {
                    "success": True,
                    "transaction_signature": str(result.value),
                    "amount_sol": amount_sol,
                    "to_wallet": to_wallet_address
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction rejected by RPC node. This may indicate insufficient funds, invalid recipient, or network issues."
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_wallet_balance(self, wallet_address: str) -> float:
        """Get the SOL balance of a wallet"""
        try:
            public_key = Pubkey.from_string(wallet_address)
            balance = self.client.get_balance(public_key)
            # Convert lamports to SOL
            return balance.value / self.LAMPORTS_PER_SOL
        except Exception as e:
            logging.error(f"Error getting balance for wallet {wallet_address}: {e}")
            return 0.0

    def get_main_wallet_balance(self) -> float:
        """Get the balance of the main wallet"""
        try:
            return self.get_wallet_balance(str(self.main_keypair.pubkey()))
        except Exception as e:
            logging.error(f"Error getting main wallet balance: {e}")
            return 0.0