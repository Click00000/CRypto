from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from web3 import Web3
import logging

logger = logging.getLogger(__name__)

# ERC20 Transfer event signature
TRANSFER_EVENT_SIGNATURE = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


class EVMParser:
    """Parse EVM blocks and extract transfers"""
    
    @staticmethod
    def parse_block(block: Dict[str, Any], labeled_addresses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse a block and extract transfers involving labeled addresses"""
        transfers = []
        
        if not block or "transactions" not in block:
            return transfers
        
        timestamp = datetime.fromtimestamp(int(block["timestamp"], 16))
        block_number = int(block["number"], 16)
        
        # Process native ETH transfers
        for tx in block["transactions"]:
            if tx.get("value") and int(tx["value"], 16) > 0:
                from_addr = tx["from"].lower()
                to_addr = tx["to"].lower() if tx.get("to") else None
                
                if not to_addr:
                    continue
                
                # Check if transfer involves labeled address
                from_exchange = labeled_addresses.get(from_addr)
                to_exchange = labeled_addresses.get(to_addr)
                
                if from_exchange or to_exchange:
                    amount = Decimal(int(tx["value"], 16)) / Decimal(10**18)  # Wei to ETH
                    
                    direction = EVMParser._determine_direction(
                        from_exchange, to_exchange, from_addr, to_addr
                    )
                    
                    transfers.append({
                        "timestamp": timestamp,
                        "chain": "EVM",
                        "tx_hash": tx["hash"],
                        "block_number": block_number,
                        "log_index": None,
                        "from_address": from_addr,
                        "to_address": to_addr,
                        "asset_symbol": "ETH",
                        "asset_address": None,
                        "amount": amount,
                        "direction": direction,
                        "exchange_from_id": from_exchange["exchange_id"] if from_exchange else None,
                        "exchange_to_id": to_exchange["exchange_id"] if to_exchange else None,
                    })
        
        return transfers
    
    @staticmethod
    def parse_receipt_logs(receipt: Dict[str, Any], block: Dict[str, Any], labeled_addresses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse transaction receipt logs for ERC20 Transfer events"""
        transfers = []
        
        if not receipt or "logs" not in receipt:
            return transfers
        
        timestamp = datetime.fromtimestamp(int(block["timestamp"], 16))
        block_number = int(block["number"], 16)
        tx_hash = receipt["transactionHash"]
        
        for log_index, log in enumerate(receipt["logs"]):
            # Check if this is a Transfer event
            if log.get("topics") and len(log["topics"]) >= 3:
                if log["topics"][0].lower() == TRANSFER_EVENT_SIGNATURE.lower():
                    # Decode Transfer event: Transfer(address indexed from, address indexed to, uint256 value)
                    from_addr = "0x" + log["topics"][1][-40:].lower()
                    to_addr = "0x" + log["topics"][2][-40:].lower()
                    amount_hex = log.get("data", "0x0")
                    amount = Decimal(int(amount_hex, 16))
                    
                    # Get token address
                    token_address = log["address"].lower()
                    
                    # Get token decimals (simplified - in production, cache this)
                    # For MVP, assume 18 decimals for most tokens
                    decimals = 18
                    amount_decimal = amount / Decimal(10**decimals)
                    
                    # Check if transfer involves labeled address
                    from_exchange = labeled_addresses.get(from_addr)
                    to_exchange = labeled_addresses.get(to_addr)
                    
                    if from_exchange or to_exchange:
                        # Get token symbol (simplified - in production, cache this)
                        # For MVP, use contract address as identifier
                        asset_symbol = f"ERC20_{token_address[:8]}"
                        
                        direction = EVMParser._determine_direction(
                            from_exchange, to_exchange, from_addr, to_addr
                        )
                        
                        transfers.append({
                            "timestamp": timestamp,
                            "chain": "EVM",
                            "tx_hash": tx_hash,
                            "block_number": block_number,
                            "log_index": log_index,
                            "from_address": from_addr,
                            "to_address": to_addr,
                            "asset_symbol": asset_symbol,
                            "asset_address": token_address,
                            "amount": amount_decimal,
                            "direction": direction,
                            "exchange_from_id": from_exchange["exchange_id"] if from_exchange else None,
                            "exchange_to_id": to_exchange["exchange_id"] if to_exchange else None,
                        })
        
        return transfers
    
    @staticmethod
    def _determine_direction(
        from_exchange: Optional[Dict],
        to_exchange: Optional[Dict],
        from_addr: str,
        to_addr: str
    ) -> str:
        """Determine transfer direction"""
        if to_exchange and not from_exchange:
            return "deposit"
        elif from_exchange and not to_exchange:
            return "withdraw"
        elif from_exchange and to_exchange:
            # Same exchange or same cluster = internal
            if from_exchange["exchange_id"] == to_exchange["exchange_id"]:
                return "internal"
            # Different exchanges = internal (exchange-to-exchange)
            return "internal"
        else:
            return "unknown"
