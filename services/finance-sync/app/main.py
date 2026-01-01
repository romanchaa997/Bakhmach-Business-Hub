#!/usr/bin/env python3
"""Finance Sync Service - Monobank API Integration"""

import os
import time
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any


class MonoClient:
    """Monobank Personal API Client"""
    
    def __init__(self, token: str, base_url: str = "https://api.monobank.ua"):
        self.token = token
        self.base_url = base_url
        self.headers = {"X-Token": token}
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information"""
        response = requests.get(
            f"{self.base_url}/personal/client-info",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_statements(
        self, 
        account_id: str, 
        from_time: int, 
        to_time: int
    ) -> List[Dict[str, Any]]:
        """Get transaction statements"""
        response = requests.get(
            f"{self.base_url}/personal/statement/{account_id}/{from_time}/{to_time}",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_exchange_rates(self) -> List[Dict[str, Any]]:
        """Get current exchange rates"""
        response = requests.get(
            f"{self.base_url}/bank/currency",
            timeout=10
        )
        response.raise_for_status()
        return response.json()


class FinanceSyncService:
    """Finance Synchronization Service"""
    
    def __init__(self, mono_token: str, data_dir: str = "./data"):
        self.client = MonoClient(mono_token)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def sync_client_info(self) -> Dict[str, Any]:
        """Sync client information"""
        try:
            info = self.client.get_client_info()
            self._save_json("client_info.json", info)
            print(f"✅ Synced client: {info.get('name', 'Unknown')}")
            return info
        except Exception as e:
            print(f"❌ Error syncing client info: {e}")
            return {}
    
    def sync_statements(self, days: int = 7) -> List[Dict[str, Any]]:
        """Sync transaction statements"""
        try:
            info = self.client.get_client_info()
            if not info.get("accounts"):
                print("⚠️ No accounts found")
                return []
            
            to_ts = int(time.time())
            from_ts = int((datetime.utcnow() - timedelta(days=days)).timestamp())
            
            all_statements = []
            for account in info["accounts"]:
                account_id = account["id"]
                statements = self.client.get_statements(account_id, from_ts, to_ts)
                all_statements.extend(statements)
                print(f"✅ Synced {len(statements)} transactions from {account['currencyCode']}")
            
            self._save_json("statements.json", all_statements)
            return all_statements
        except Exception as e:
            print(f"❌ Error syncing statements: {e}")
            return []
    
    def _save_json(self, filename: str, data: Any) -> None:
        """Save data to JSON file"""
        filepath = self.data_dir / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)


def main():
    """Main entry point"""
    token = os.getenv("MONO_TOKEN")
    if not token:
        raise RuntimeError("MONO_TOKEN env var is required")
    
    service = FinanceSyncService(token)
    
    # Sync data
    service.sync_client_info()
    service.sync_statements(days=7)
    
    print("\n✅ Finance sync completed successfully!")


if __name__ == "__main__":
    main()
