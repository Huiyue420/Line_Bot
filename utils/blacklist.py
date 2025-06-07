import json
import os
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger('blacklist')

class BlacklistManager:
    def __init__(self, blacklist_file: str = 'blacklist.json'):
        self.blacklist_file = blacklist_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """確保黑名單檔案存在"""
        if not os.path.exists(self.blacklist_file):
            with open(self.blacklist_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'users': [],
                    'history': []
                }, f, ensure_ascii=False, indent=2)

    def load_blacklist(self) -> dict:
        """載入黑名單"""
        try:
            with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入黑名單失敗: {e}")
            return {'users': [], 'history': []}

    def save_blacklist(self, data: dict):
        """儲存黑名單"""
        try:
            with open(self.blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"儲存黑名單失敗: {e}")

    def add_to_blacklist(self, user_id: str, reason: str, operator: Optional[str] = None) -> bool:
        """新增用戶到黑名單"""
        try:
            data = self.load_blacklist()
            
            if user_id not in data['users']:
                data['users'].append(user_id)
                data['history'].append({
                    'action': 'add',
                    'user_id': user_id,
                    'reason': reason,
                    'operator': operator,
                    'timestamp': datetime.now().isoformat()
                })
                
                self.save_blacklist(data)
                logger.info(f"已將用戶加入黑名單: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"加入黑名單失敗: {e}")
            return False

    def remove_from_blacklist(self, user_id: str, reason: str, operator: Optional[str] = None) -> bool:
        """從黑名單移除用戶"""
        try:
            data = self.load_blacklist()
            
            if user_id in data['users']:
                data['users'].remove(user_id)
                data['history'].append({
                    'action': 'remove',
                    'user_id': user_id,
                    'reason': reason,
                    'operator': operator,
                    'timestamp': datetime.now().isoformat()
                })
                
                self.save_blacklist(data)
                logger.info(f"已將用戶從黑名單移除: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"從黑名單移除失敗: {e}")
            return False

    def is_blacklisted(self, user_id: str) -> bool:
        """檢查用戶是否在黑名單中"""
        try:
            data = self.load_blacklist()
            return user_id in data['users']
        except Exception as e:
            logger.error(f"檢查黑名單失敗: {e}")
            return False

    def get_blacklist(self) -> List[str]:
        """獲取所有黑名單用戶"""
        try:
            data = self.load_blacklist()
            return data['users']
        except Exception as e:
            logger.error(f"獲取黑名單失敗: {e}")
            return []

    def get_history(self) -> List[dict]:
        """獲取黑名單操作歷史"""
        try:
            data = self.load_blacklist()
            return data['history']
        except Exception as e:
            logger.error(f"獲取歷史記錄失敗: {e}")
            return [] 