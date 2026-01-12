from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.ingestion.btc.core_rpc import BitcoinCoreRPC
from app.ingestion.btc.explorer_api import BitcoinExplorerAPI
from app.db.models import LabeledAddress, SyncState, RawTransfer, Chain
from app.core.config import settings
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

BATCH_SIZE = 5  # Smaller batch for BTC


class BTCSync:
    """Bitcoin sync service with adapter pattern"""
    
    def __init__(self, db: Session):
        self.db = db
        self.adapter = self._get_adapter()
    
    def _get_adapter(self):
        """Get BTC adapter based on mode"""
        if settings.BTC_MODE == "CORE_RPC":
            return BitcoinCoreRPC()
        elif settings.BTC_MODE == "EXPLORER":
            return BitcoinExplorerAPI()
        else:
            raise ValueError(f"Invalid BTC_MODE: {settings.BTC_MODE}")
    
    def sync(self) -> Dict[str, Any]:
        """Sync Bitcoin - process new blocks"""
        # Get sync state
        sync_state = self.db.query(SyncState).filter(SyncState.chain == Chain.BTC).first()
        if not sync_state:
            sync_state = SyncState(chain=Chain.BTC, last_processed_height=None)
            self.db.add(sync_state)
            self.db.commit()
        
        # Get labeled addresses
        labeled_addresses = self._get_labeled_addresses()
        if not labeled_addresses:
            logger.info("No labeled addresses found for BTC")
            return {"processed": 0, "transfers": 0, "last_height": sync_state.last_processed_height}
        
        # Get latest height
        try:
            if settings.BTC_MODE == "CORE_RPC":
                latest_height = self.adapter.get_block_count()
            else:
                latest_height = self.adapter.get_tip_height()
        except Exception as e:
            logger.error(f"Failed to get latest height: {e}")
            return {"error": str(e)}
        
        # Determine start height
        start_height = sync_state.last_processed_height + 1 if sync_state.last_processed_height else latest_height - BATCH_SIZE
        
        if start_height > latest_height:
            logger.info(f"No new blocks to process. Latest: {latest_height}, Last processed: {sync_state.last_processed_height}")
            return {"processed": 0, "transfers": 0, "last_height": sync_state.last_processed_height}
        
        # Process blocks
        end_height = min(start_height + BATCH_SIZE - 1, latest_height)
        processed_count = 0
        transfer_count = 0
        
        for height in range(start_height, end_height + 1):
            try:
                # Get block
                if settings.BTC_MODE == "CORE_RPC":
                    block_hash = self.adapter.get_block_hash(height)
                    block = self.adapter.get_block(block_hash, verbosity=2)
                else:
                    block_hash = self.adapter.get_block_hash(height)
                    block = self.adapter.get_block(block_hash)
                
                if not block:
                    continue
                
                # Parse block for transfers
                transfers = self._parse_block(block, labeled_addresses, height)
                
                # Save transfers
                for transfer_data in transfers:
                    transfer = RawTransfer(**transfer_data)
                    self.db.add(transfer)
                    transfer_count += 1
                
                processed_count += 1
                
                # Update sync state
                sync_state.last_processed_height = height
                self.db.commit()
                
            except Exception as e:
                logger.error(f"Failed to process block {height}: {e}")
                self.db.rollback()
                break
        
        return {
            "processed": processed_count,
            "transfers": transfer_count,
            "last_height": sync_state.last_processed_height
        }
    
    def _parse_block(self, block: Dict[str, Any], labeled_addresses: Dict[str, Dict], height: int) -> List[Dict[str, Any]]:
        """Parse Bitcoin block and extract transfers involving labeled addresses"""
        transfers = []
        
        # Get timestamp
        if settings.BTC_MODE == "CORE_RPC":
            timestamp = datetime.fromtimestamp(block.get("time", 0))
            tx_list = block.get("tx", [])
        else:
            # Explorer API format
            timestamp = datetime.fromtimestamp(block.get("timestamp", 0))
            tx_list = block.get("tx", [])
        
        # Process transactions
        for tx in tx_list:
            txid = tx.get("txid") or tx.get("hash")
            if not txid:
                continue
            
            # Get full transaction details
            try:
                if settings.BTC_MODE == "CORE_RPC":
                    full_tx = self.adapter.get_transaction(txid, verbose=True)
                else:
                    full_tx = self.adapter.get_transaction(txid)
            except Exception as e:
                logger.warning(f"Failed to get full tx {txid}: {e}")
                continue
            
            # Parse inputs and outputs
            vin = full_tx.get("vin", [])
            vout = full_tx.get("vout", [])
            
            # Track addresses in this transaction
            involved_addresses = set()
            address_to_exchange = {}
            
            # Check outputs
            for output in vout:
                script_pubkey = output.get("scriptPubKey", {})
                addresses = script_pubkey.get("addresses", [])
                if not addresses:
                    # Try single address field
                    addr = script_pubkey.get("address")
                    if addr:
                        addresses = [addr]
                
                for addr in addresses:
                    if addr in labeled_addresses:
                        involved_addresses.add(addr)
                        address_to_exchange[addr] = labeled_addresses[addr]
            
            # Check inputs (previous outputs)
            for input_tx in vin:
                prev_txid = input_tx.get("txid")
                vout_index = input_tx.get("vout")
                
                if prev_txid and vout_index is not None:
                    try:
                        prev_tx = self.adapter.get_transaction(prev_txid)
                        prev_output = prev_tx.get("vout", [])[vout_index] if vout_index < len(prev_tx.get("vout", [])) else None
                        if prev_output:
                            script_pubkey = prev_output.get("scriptPubKey", {})
                            addresses = script_pubkey.get("addresses", [])
                            if not addresses:
                                addr = script_pubkey.get("address")
                                if addr:
                                    addresses = [addr]
                            
                            for addr in addresses:
                                if addr in labeled_addresses:
                                    involved_addresses.add(addr)
                                    address_to_exchange[addr] = labeled_addresses[addr]
                    except Exception as e:
                        logger.debug(f"Could not fetch prev tx {prev_txid}: {e}")
            
            # If transaction involves labeled addresses, record it
            if involved_addresses:
                # Calculate total value
                total_value = Decimal(0)
                for output in vout:
                    value = output.get("value", 0)
                    if isinstance(value, (int, float)):
                        total_value += Decimal(value)
                
                if total_value > 0:
                    # Determine direction (simplified - in production, track more precisely)
                    direction = "unknown"
                    exchange_from_id = None
                    exchange_to_id = None
                    
                    # For MVP, if any labeled address is involved, record as deposit/withdraw
                    # More sophisticated logic can be added later
                    if len(involved_addresses) == 1:
                        addr = list(involved_addresses)[0]
                        exchange_info = address_to_exchange[addr]
                        # Assume it's a deposit if it appears in outputs
                        direction = "deposit"
                        exchange_to_id = exchange_info["exchange_id"]
                    else:
                        # Multiple addresses - could be internal or exchange-to-exchange
                        direction = "internal"
                    
                    transfers.append({
                        "timestamp": timestamp,
                        "chain": "BTC",
                        "tx_hash": txid,
                        "block_number": height,
                        "log_index": None,
                        "from_address": "",  # BTC doesn't have explicit from
                        "to_address": list(involved_addresses)[0] if involved_addresses else "",
                        "asset_symbol": "BTC",
                        "asset_address": None,
                        "amount": total_value,
                        "direction": direction,
                        "exchange_from_id": exchange_from_id,
                        "exchange_to_id": exchange_to_id,
                    })
        
        return transfers
    
    def _get_labeled_addresses(self) -> Dict[str, Dict[str, Any]]:
        """Get labeled addresses as dict for fast lookup"""
        addresses = self.db.query(LabeledAddress).filter(
            LabeledAddress.chain == Chain.BTC,
            LabeledAddress.is_active == True
        ).all()
        
        result = {}
        for addr in addresses:
            result[addr.address] = {
                "exchange_id": str(addr.exchange_id),
                "cluster_id": str(addr.cluster_id) if addr.cluster_id else None,
                "label": addr.label.value
            }
        
        return result
