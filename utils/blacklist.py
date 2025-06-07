import json
import os
from datetime import datetime
import logging
from typing import List, Dict, Optional

logger = logging.getLogger('blacklist')

class BlacklistManager:
    def __init__(self, blacklist_file: str = 'data/blacklist.json'):
        """初始化黑名單管理器"""
        self.blacklist_file = blacklist_file
        self.blacklist: Dict[str, dict] = {}
        self.history: List[dict] = []
        
        # 確保資料目錄存在
        os.makedirs(os.path.dirname(blacklist_file), exist_ok=True)
        
        # 載入黑名單
        self.load_blacklist()

    def load_blacklist(self):
        """從檔案載入黑名單"""
        try:
            if os.path.exists(self.blacklist_file):
                with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.blacklist = data.get('blacklist', {})
                    self.history = data.get('history', [])
        except Exception as e:
            logger.error(f"載入黑名單失敗: {e}")
            self.blacklist = {}
            self.history = []

    def save_blacklist(self):
        """儲存黑名單到檔案"""
        try:
            data = {
                'blacklist': self.blacklist,
                'history': self.history
            }
            with open(self.blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"儲存黑名單失敗: {e}")

    def add_to_blacklist(self, user_id: str, reason: str, reporter_id: Optional[str] = None) -> bool:
        """
        新增用戶到黑名單
        :param user_id: 用戶 ID
        :param reason: 封鎖原因
        :param reporter_id: 回報者 ID（可選）
        :return: 是否成功
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # 新增到黑名單
            self.blacklist[user_id] = {
                'reason': reason,
                'timestamp': timestamp,
                'reporter_id': reporter_id
            }
            
            # 記錄操作歷史
            self.history.append({
                'action': 'add',
                'user_id': user_id,
                'reason': reason,
                'reporter_id': reporter_id,
                'timestamp': timestamp
            })
            
            # 儲存變更
            self.save_blacklist()
            logger.info(f"已將用戶 {user_id} 加入黑名單")
            return True
            
        except Exception as e:
            logger.error(f"新增黑名單失敗: {e}")
            return False

    def remove_from_blacklist(self, user_id: str, reason: str, remover_id: Optional[str] = None) -> bool:
        """
        從黑名單移除用戶
        :param user_id: 用戶 ID
        :param reason: 解除原因
        :param remover_id: 解除者 ID（可選）
        :return: 是否成功
        """
        try:
            if user_id in self.blacklist:
                # 從黑名單移除
                del self.blacklist[user_id]
                
                # 記錄操作歷史
                self.history.append({
                    'action': 'remove',
                    'user_id': user_id,
                    'reason': reason,
                    'remover_id': remover_id,
                    'timestamp': datetime.now().isoformat()
                })
                
                # 儲存變更
                self.save_blacklist()
                logger.info(f"已將用戶 {user_id} 從黑名單移除")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"移除黑名單失敗: {e}")
            return False

    def is_blacklisted(self, user_id: str) -> bool:
        """檢查用戶是否在黑名單中"""
        return user_id in self.blacklist

    def get_blacklist(self) -> Dict[str, dict]:
        """取得完整黑名單"""
        return self.blacklist

    def get_blacklist_reason(self, user_id: str) -> Optional[str]:
        """取得用戶被加入黑名單的原因"""
        if user_id in self.blacklist:
            return self.blacklist[user_id]['reason']
        return None

    def get_history(self, limit: int = None) -> List[dict]:
        """
        取得操作歷史
        :param limit: 限制回傳數量（可選）
        :return: 操作歷史列表
        """
        if limit:
            return self.history[-limit:]
        return self.history

    def export_blacklist(self, output_file: str) -> bool:
        """匯出黑名單到指定檔案"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'blacklist': self.blacklist,
                    'history': self.history
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"匯出黑名單失敗: {e}")
            return False

    def import_blacklist(self, input_file: str) -> bool:
        """從檔案匯入黑名單"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.blacklist.update(data.get('blacklist', {}))
                self.history.extend(data.get('history', []))
            self.save_blacklist()
            return True
        except Exception as e:
            logger.error(f"匯入黑名單失敗: {e}")
            return False 