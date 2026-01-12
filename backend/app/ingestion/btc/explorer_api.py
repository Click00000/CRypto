import requests
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class BitcoinExplorerAPI:
    """Bitcoin Explorer API client (e.g., Blockstream)"""
    
    def __init__(self):
        self.base_url = settings.BTC_EXPLORER_BASE_URL.rstrip("/")
        self.api_key = settings.BTC_EXPLORER_API_KEY
    
    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """Make GET request to explorer API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {}
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Explorer API call failed: {endpoint} - {e}")
            raise
    
    def get_tip_height(self) -> int:
        """Get latest block height"""
        try:
            # Blockstream API: GET /blocks/tip/height
            height = self._get("/blocks/tip/height")
            return int(height)
        except Exception as e:
            logger.error(f"Failed to get tip height: {e}")
            raise
    
    def get_block_hash(self, height: int) -> str:
        """Get block hash by height"""
        try:
            # Blockstream API: GET /block-height/{height}
            hash_str = self._get(f"/block-height/{height}")
            return hash_str
        except Exception as e:
            logger.error(f"Failed to get block hash: {e}")
            raise
    
    def get_block(self, block_hash: str) -> Dict[str, Any]:
        """Get block by hash"""
        try:
            # Blockstream API: GET /block/{hash}
            return self._get(f"/block/{block_hash}")
        except Exception as e:
            logger.error(f"Failed to get block: {e}")
            raise
    
    def get_transaction(self, txid: str) -> Dict[str, Any]:
        """Get transaction by ID"""
        try:
            # Blockstream API: GET /tx/{txid}
            return self._get(f"/tx/{txid}")
        except Exception as e:
            logger.error(f"Failed to get transaction: {e}")
            raise
