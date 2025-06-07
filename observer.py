import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging
from linebot import LineBotApi
from line_py import LineClient  # 請注意：這是非官方套件，需要額外安裝

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='observer.log'
)
logger = logging.getLogger('observer')

class GroupObserver:
    def __init__(self, line_bot_token: str, line_account: str, line_password: str):
        self.official_api = LineBotApi(line_bot_token)
        self.client = None
        self.line_account = line_account
        self.line_password = line_password
        self.group_states: Dict[str, dict] = {}
        self.initialize_client()

    def initialize_client(self):
        """初始化非官方客戶端"""
        try:
            self.client = LineClient(self.line_account, self.line_password)
            logger.info("非官方客戶端初始化成功")
        except Exception as e:
            logger.error(f"非官方客戶端初始化失敗: {e}")
            self.client = None

    def get_group_state(self, group_id: str) -> dict:
        """獲取群組當前狀態"""
        try:
            state = {
                'members': [],
                'album_count': 0,
                'announcement': '',
                'timestamp': datetime.now().isoformat()
            }

            # 使用官方 API 獲取基本資訊
            if self.official_api:
                try:
                    group_summary = self.official_api.get_group_summary(group_id)
                    state['group_name'] = group_summary.group_name
                    state['member_count'] = group_summary.members_count
                except Exception as e:
                    logger.error(f"獲取群組資訊失敗 (官方 API): {e}")

            # 使用非官方客戶端獲取詳細資訊
            if self.client:
                try:
                    group = self.client.get_group(group_id)
                    state['members'] = [m.mid for m in group.members]
                    state['album_count'] = len(group.albums)
                    state['announcement'] = group.announcement
                except Exception as e:
                    logger.error(f"獲取群組資訊失敗 (非官方): {e}")

            return state
        except Exception as e:
            logger.error(f"獲取群組狀態失敗: {e}")
            return {}

    def detect_changes(self, group_id: str) -> dict:
        """檢測群組變更"""
        current_state = self.get_group_state(group_id)
        previous_state = self.group_states.get(group_id, {})
        changes = {
            'kicked_members': [],
            'album_changed': False,
            'announcement_changed': False,
            'timestamp': datetime.now().isoformat()
        }

        if previous_state:
            # 檢測成員變化
            old_members = set(previous_state.get('members', []))
            new_members = set(current_state.get('members', []))
            kicked_members = old_members - new_members
            if kicked_members:
                changes['kicked_members'] = list(kicked_members)

            # 檢測相簿變化
            if current_state.get('album_count') != previous_state.get('album_count'):
                changes['album_changed'] = True

            # 檢測公告變化
            if current_state.get('announcement') != previous_state.get('announcement'):
                changes['announcement_changed'] = True

        # 更新狀態
        self.group_states[group_id] = current_state
        return changes

    def save_changes(self, group_id: str, changes: dict):
        """儲存變更記錄"""
        if any(changes.values()):
            log_file = f'logs/group_{group_id}_{datetime.now().strftime("%Y%m%d")}.json'
            os.makedirs('logs', exist_ok=True)
            
            try:
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                else:
                    logs = []
                
                logs.append(changes)
                
                with open(log_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, ensure_ascii=False, indent=2)
                
                logger.info(f"變更記錄已儲存: {log_file}")
            except Exception as e:
                logger.error(f"儲存變更記錄失敗: {e}")

    def run(self, group_ids: List[str], interval: int = 60):
        """開始監控群組"""
        logger.info(f"開始監控群組: {group_ids}")
        
        while True:
            for group_id in group_ids:
                try:
                    changes = self.detect_changes(group_id)
                    if any(changes.values()):
                        logger.info(f"偵測到群組變更 {group_id}: {changes}")
                        self.save_changes(group_id, changes)
                except Exception as e:
                    logger.error(f"監控群組時發生錯誤 {group_id}: {e}")
            
            time.sleep(interval)

if __name__ == "__main__":
    # 從環境變數獲取設定
    LINE_BOT_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_ACCOUNT = os.getenv('LINE_OBSERVER_ACCOUNT')
    LINE_PASSWORD = os.getenv('LINE_OBSERVER_PASSWORD')
    GROUP_IDS = os.getenv('TARGET_GROUP_IDS', '').split(',')

    if not all([LINE_BOT_TOKEN, LINE_ACCOUNT, LINE_PASSWORD, GROUP_IDS]):
        logger.error("缺少必要的環境變數設定")
        exit(1)

    observer = GroupObserver(LINE_BOT_TOKEN, LINE_ACCOUNT, LINE_PASSWORD)
    observer.run(GROUP_IDS) 