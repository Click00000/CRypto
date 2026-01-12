from sqlalchemy.orm import Session
from typing import Dict, Any
from app.ingestion.evm.rpc_client import EVMRPCClient
from app.ingestion.evm.parser import EVMParser
from app.db.models import LabeledAddress, SyncState, RawTransfer, Chain
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Safe batch size
BATCH_SIZE = 10


class EVMSync:
    """EVM chain sync service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rpc_client = EVMRPCClient()
        self.parser = EVMParser()
    
    def sync(self) -> Dict[str, Any]:
        """Sync EVM chain - process new blocks"""
        # Get sync state
        sync_state = self.db.query(SyncState).filter(SyncState.chain == Chain.EVM).first()
        if not sync_state:
            sync_state = SyncState(chain=Chain.EVM, last_processed_block=None)
            self.db.add(sync_state)
            self.db.commit()
        
        # Get labeled addresses
        labeled_addresses = self._get_labeled_addresses()
        if not labeled_addresses:
            logger.info("No labeled addresses found for EVM")
            return {"processed": 0, "transfers": 0, "last_block": sync_state.last_processed_block}
        
        # Get latest block
        try:
            latest_block = self.rpc_client.get_latest_block_number()
        except Exception as e:
            logger.error(f"Failed to get latest block: {e}")
            return {"error": str(e)}
        
        # Determine start block
        start_block = sync_state.last_processed_block + 1 if sync_state.last_processed_block else latest_block - BATCH_SIZE
        
        if start_block > latest_block:
            logger.info(f"No new blocks to process. Latest: {latest_block}, Last processed: {sync_state.last_processed_block}")
            return {"processed": 0, "transfers": 0, "last_block": sync_state.last_processed_block}
        
        # Process blocks in batches
        end_block = min(start_block + BATCH_SIZE - 1, latest_block)
        processed_count = 0
        transfer_count = 0
        
        for block_num in range(start_block, end_block + 1):
            try:
                block = self.rpc_client.get_block(block_num, full_transactions=True)
                if not block:
                    continue
                
                # Parse native ETH transfers
                transfers = self.parser.parse_block(block, labeled_addresses)
                
                # Parse ERC20 transfers from receipts
                for tx in block.get("transactions", []):
                    if tx.get("hash"):
                        try:
                            receipt = self.rpc_client.get_transaction_receipt(tx["hash"])
                            if receipt:
                                erc20_transfers = self.parser.parse_receipt_logs(receipt, block, labeled_addresses)
                                transfers.extend(erc20_transfers)
                        except Exception as e:
                            logger.warning(f"Failed to get receipt for {tx['hash']}: {e}")
                
                # Save transfers
                for transfer_data in transfers:
                    transfer = RawTransfer(**transfer_data)
                    self.db.add(transfer)
                    transfer_count += 1
                
                processed_count += 1
                
                # Update sync state every block
                sync_state.last_processed_block = block_num
                self.db.commit()
                
            except Exception as e:
                logger.error(f"Failed to process block {block_num}: {e}")
                self.db.rollback()
                break
        
        return {
            "processed": processed_count,
            "transfers": transfer_count,
            "last_block": sync_state.last_processed_block
        }
    
    def _get_labeled_addresses(self) -> Dict[str, Dict[str, Any]]:
        """Get labeled addresses as dict for fast lookup"""
        addresses = self.db.query(LabeledAddress).filter(
            LabeledAddress.chain == Chain.EVM,
            LabeledAddress.is_active == True
        ).all()
        
        result = {}
        for addr in addresses:
            normalized = addr.address.lower()
            result[normalized] = {
                "exchange_id": str(addr.exchange_id),
                "cluster_id": str(addr.cluster_id) if addr.cluster_id else None,
                "label": addr.label.value
            }
        
        return result
