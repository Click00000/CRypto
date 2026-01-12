import requests
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class BitcoinCoreRPC:
    """Bitcoin Core RPC client"""
    
    def __init__(self):
        self.rpc_url = settings.BTC_RPC_URL
        self.rpc_user = settings.BTC_RPC_USER
        self.rpc_pass = settings.BTC_RPC_PASS
    
    def _call(self, method: str, params: List[Any] = None) -> Any:
        """Make Bitcoin Core RPC call"""
        if params is None:
            params = []
        
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 1
        }
        
        try:
            response = requests.post(
                self.rpc_url,
                json=payload,
                auth=(self.rpc_user, self.rpc_pass),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data and data["error"]:
                raise Exception(f"RPC Error: {data['error']}")
            
            return data.get("result")
        except Exception as e:
            logger.error(f"Bitcoin RPC call failed: {method} - {e}")
            raise
    
    def get_block_count(self) -> int:
        """Get latest block height"""
        return self._call("getblockcount")
    
    def get_block_hash(self, height: int) -> str:
        """Get block hash by height"""
        return self._call("getblockhash", [height])
    
    def get_block(self, block_hash: str, verbosity: int = 2) -> Dict[str, Any]:
        """Get block by hash"""
        return self._call("getblock", [block_hash, verbosity])
    
    def get_transaction(self, txid: str, verbose: bool = True) -> Dict[str, Any]:
        """Get transaction by ID"""
        return self._call("getrawtransaction", [txid, verbose])
