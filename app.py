import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    JoinEvent, LeaveEvent, MemberJoinedEvent, MemberLeftEvent
)
from datetime import datetime
import json
import threading
from utils.blacklist import BlacklistManager
from observer import GroupObserver

app = Flask(__name__)

# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)
LINE_OBSERVER_ACCOUNT = os.getenv('LINE_OBSERVER_ACCOUNT', None)
LINE_OBSERVER_PASSWORD = os.getenv('LINE_OBSERVER_PASSWORD', None)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
blacklist_manager = BlacklistManager()

# 管理員清單
ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',')

def is_admin(user_id: str) -> bool:
    """檢查是否為管理員"""
    return user_id in ADMIN_IDS

def start_observer(group_ids):
    """啟動群組觀察者"""
    observer = GroupObserver(
        LINE_CHANNEL_ACCESS_TOKEN,
        LINE_OBSERVER_ACCOUNT,
        LINE_OBSERVER_PASSWORD
    )
    observer.run(group_ids)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    for member in event.joined.members:
        if blacklist_manager.is_blacklisted(member.user_id):
            try:
                # 踢出黑名單用戶
                line_bot_api.kickoutFromGroup(event.source.group_id, member.user_id)
                # 取得邀請者資訊
                if event.source.type == "group":
                    group_member_ids = line_bot_api.get_group_member_ids(event.source.group_id)
                    # 這裡需要實作取得邀請者的邏輯
            except Exception as e:
                print(f"Error kicking user: {e}")

@handler.add(MemberLeftEvent)
def handle_member_left(event):
    # 記錄踢人事件
    print(f"Member left event: {event}")

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    user_id = event.source.user_id

    # 只處理管理員的指令
    if not is_admin(user_id):
        return

    if text == "!黑名單":
        blacklist = blacklist_manager.get_blacklist()
        response = "黑名單列表：\n" + "\n".join(blacklist) if blacklist else "黑名單為空"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

    elif text.startswith("!封鎖 "):
        target_id = text.split(" ")[1]
        if blacklist_manager.add_to_blacklist(target_id, "管理員手動封鎖", user_id):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"已將用戶 {target_id} 加入黑名單")
            )
            # 如果在群組中，立即踢出
            if event.source.type == "group":
                try:
                    line_bot_api.kickoutFromGroup(event.source.group_id, target_id)
                except Exception as e:
                    print(f"Error kicking user: {e}")

    elif text.startswith("!解除 "):
        target_id = text.split(" ")[1]
        if blacklist_manager.remove_from_blacklist(target_id, "管理員手動解除", user_id):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"已將用戶 {target_id} 從黑名單移除")
            )

    elif text == "!歷史記錄":
        history = blacklist_manager.get_history()
        response = "操作歷史：\n" + "\n".join(
            f"{h['timestamp']}: {h['action']} {h['user_id']} ({h['reason']})"
            for h in history[-10:]  # 只顯示最近10筆
        ) if history else "無操作歷史"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

if __name__ == "__main__":
    # 啟動觀察者（在背景執行）
    if LINE_OBSERVER_ACCOUNT and LINE_OBSERVER_PASSWORD:
        observer_thread = threading.Thread(
            target=start_observer,
            args=([os.getenv('TARGET_GROUP_IDS', '').split(',')]),
            daemon=True
        )
        observer_thread.start()
    
    app.run(debug=True) 