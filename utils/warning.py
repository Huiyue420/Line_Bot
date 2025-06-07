from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class WarningManager:
    def __init__(self, blacklist_manager):
        self.warning_file = "data/warnings.json"
        self.warnings: Dict[str, Dict[str, List[Dict]]] = {}  # group_id -> user_id -> list of warnings
        self.blacklist_manager = blacklist_manager
        self.max_warnings = 3
        self._load_warnings()

    def _load_warnings(self) -> None:
        """從檔案載入警告資料"""
        try:
            if os.path.exists(self.warning_file):
                with open(self.warning_file, 'r', encoding='utf-8') as f:
                    self.warnings = json.load(f)
        except Exception as e:
            print(f"載入警告資料時發生錯誤: {e}")
            self.warnings = {}

    def _save_warnings(self) -> None:
        """儲存警告資料到檔案"""
        try:
            os.makedirs(os.path.dirname(self.warning_file), exist_ok=True)
            with open(self.warning_file, 'w', encoding='utf-8') as f:
                json.dump(self.warnings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存警告資料時發生錯誤: {e}")

    def add_warning(self, group_id: str, user_id: str, reason: str, warned_by: str) -> Dict:
        """新增警告"""
        if group_id not in self.warnings:
            self.warnings[group_id] = {}
        
        if user_id not in self.warnings[group_id]:
            self.warnings[group_id][user_id] = []

        warning = {
            'reason': reason,
            'warned_by': warned_by,
            'timestamp': datetime.now().isoformat()
        }
        
        self.warnings[group_id][user_id].append(warning)
        self._save_warnings()

        warning_count = len(self.warnings[group_id][user_id])
        
        # 檢查是否達到最大警告次數
        if warning_count >= self.max_warnings:
            self.blacklist_manager.add_to_blacklist(
                user_id,
                f"達到最大警告次數 ({self.max_warnings} 次)",
                None
            )
            return {
                'status': 'blacklisted',
                'warning_count': warning_count,
                'warning': warning
            }
        
        return {
            'status': 'warned',
            'warning_count': warning_count,
            'warning': warning
        }

    def remove_warning(self, group_id: str, user_id: str) -> bool:
        """移除最後一次警告"""
        if (group_id not in self.warnings or 
            user_id not in self.warnings[group_id] or 
            not self.warnings[group_id][user_id]):
            return False

        self.warnings[group_id][user_id].pop()
        
        # 如果沒有警告了，清理資料結構
        if not self.warnings[group_id][user_id]:
            del self.warnings[group_id][user_id]
            if not self.warnings[group_id]:
                del self.warnings[group_id]
        
        self._save_warnings()
        return True

    def get_warnings(self, group_id: str, user_id: str) -> List[Dict]:
        """取得用戶的警告列表"""
        return self.warnings.get(group_id, {}).get(user_id, []) 