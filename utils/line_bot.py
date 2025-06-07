from linebot import LineBotApi
from linebot.models import (
    TextSendMessage,
    StickerSendMessage,
    ImageSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageAction
)
from linebot.exceptions import LineBotApiError
import logging
from datetime import datetime
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest,
    ReplyMessageRequest
)

logger = logging.getLogger('line_bot')

class LineBotManager:
    def __init__(self, channel_access_token: str):
        """初始化 LINE Bot 管理器"""
        configuration = Configuration(access_token=channel_access_token)
        self.client = ApiClient(configuration)
        self.api = MessagingApi(self.client)

    def send_message(self, to: str, text: str) -> bool:
        """發送訊息到指定目標"""
        try:
            self.api.push_message(
                PushMessageRequest(
                    to=to,
                    messages=[TextMessage(text=text)]
                )
            )
            return True
        except Exception as e:
            print(f"發送訊息失敗: {e}")
            return False

    def reply_message(self, reply_token: str, text: str) -> bool:
        """回覆訊息"""
        try:
            self.api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=text)]
                )
            )
            return True
        except Exception as e:
            print(f"回覆訊息失敗: {e}")
            return False

    def send_warning(self, to: str, message: str) -> bool:
        """發送警告訊息"""
        warning_message = f"""
⚠️ 警告通知
-------------------
{message}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        try:
            messages = [
                TextSendMessage(text=warning_message),
                StickerSendMessage(
                    package_id='2',
                    sticker_id='17'
                )
            ]
            self.api.push_message(
                PushMessageRequest(
                    to=to,
                    messages=messages
                )
            )
            return True
        except Exception as e:
            print(f"發送警告失敗: {e}")
            return False

    def send_alert(self, to: str, text: str) -> bool:
        """發送警告訊息"""
        return self.send_message(to, text)

    def send_confirmation(self, to: str, message: str, actions: list) -> bool:
        """發送確認按鈕訊息"""
        try:
            message_actions = [MessageAction(label=label, text=text) 
                             for label, text in actions]
            
            confirm_template = ButtonsTemplate(
                text=message,
                actions=message_actions
            )
            
            template_message = TemplateSendMessage(
                alt_text='確認訊息',
                template=confirm_template
            )
            
            self.api.push_message(
                PushMessageRequest(
                    to=to,
                    messages=[template_message]
                )
            )
            return True
        except Exception as e:
            print(f"發送確認訊息失敗: {e}")
            return False

    def get_group_member_ids(self, group_id: str) -> list:
        """獲取群組成員 ID 列表"""
        try:
            member_ids = self.api.get_group_member_ids(group_id)
            return member_ids
        except Exception as e:
            print(f"獲取群組成員失敗: {e}")
            return []

    def get_group_member_profile(self, group_id: str, user_id: str) -> dict:
        """取得群組成員資料"""
        try:
            profile = self.api.get_group_member_profile(group_id, user_id)
            return {
                'user_id': profile.user_id,
                'display_name': profile.display_name,
                'picture_url': profile.picture_url
            }
        except Exception as e:
            print(f"取得群組成員資料失敗: {e}")
            return None

    def kick_user(self, group_id: str, user_id: str) -> bool:
        """將用戶踢出群組"""
        try:
            self.api.leave_group_v2(group_id, user_id)
            return True
        except Exception as e:
            print(f"踢出用戶失敗: {e}")
            return False 