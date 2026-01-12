import requests
import logging
from typing import Dict, Any, Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class EVMRPCClient:
    """EVM JSON-RPC client"""
    
    def __init__(self, rpc_url: str = None):
        self.rpc_url = rpc_url or settings.EVM_RPC_URL
    
    def _call(self, method: str, params: List[Any]) -> Dict[str, Any]:
        """Make JSON-RPC call"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        try:
            response = requests.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise Exception(f"RPC Error: {data['error']}")
            
            return data.get("result")
        except Exception as e:
            logger.error(f"RPC call failed: {method} - {e}")
            raise
    
    def get_latest_block_number(self) -> int:
        """Get latest block number"""
        result = self._call("eth_blockNumber", [])
        return int(result, 16)
    
    def get_block(self, block_number: int, full_transactions: bool = True) -> Dict[str, Any]:
        """Get block by number"""
        hex_block = hex(block_number)
        result = self._call("eth_getBlockByNumber", [hex_block, full_transactions])
        return result
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction receipt"""
        result = self._call("eth_getTransactionReceipt", [tx_hash])
        return result
