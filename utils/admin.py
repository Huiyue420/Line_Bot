from typing import Dict, Set, Optional
import json
import os
from datetime import datetime

class AdminManager:
    def __init__(self):
        self.admin_file = "data/admins.json"
        self.admins: Dict[str, Set[str]] = {}  # group_id -> set of admin user_ids
        self._load_admins()

    def _load_admins(self) -> None:
        """從檔案載入管理員資料"""
        try:
            if os.path.exists(self.admin_file):
                with open(self.admin_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.admins = {group_id: set(admins) for group_id, admins in data.items()}
        except Exception as e:
            print(f"載入管理員資料時發生錯誤: {e}")
            self.admins = {}

    def _save_admins(self) -> None:
        """儲存管理員資料到檔案"""
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(self.admin_file), exist_ok=True)
            
            # 將 set 轉換為 list 以便 JSON 序列化
            data = {group_id: list(admins) for group_id, admins in self.admins.items()}
            
            with open(self.admin_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存管理員資料時發生錯誤: {e}")

    def is_admin(self, group_id: str, user_id: str) -> bool:
        """檢查用戶是否為群組管理員"""
        return user_id in self.admins.get(group_id, set())

    def add_admin(self, group_id: str, user_id: str) -> bool:
        """新增群組管理員"""
        if group_id not in self.admins:
            self.admins[group_id] = set()
        
        if user_id in self.admins[group_id]:
            return False
        
        self.admins[group_id].add(user_id)
        self._save_admins()
        return True

    def remove_admin(self, group_id: str, user_id: str) -> bool:
        """移除群組管理員"""
        if group_id not in self.admins or user_id not in self.admins[group_id]:
            return False
        
        self.admins[group_id].remove(user_id)
        self._save_admins()
        return True

    def get_admins(self, group_id: str) -> Set[str]:
        """取得群組所有管理員"""
        return self.admins.get(group_id, set())

    def initialize_group(self, group_id: str, creator_id: str) -> None:
        """初始化群組，將建立者設為管理員"""
        if group_id not in self.admins:
            self.admins[group_id] = {creator_id}
            self._save_admins() 