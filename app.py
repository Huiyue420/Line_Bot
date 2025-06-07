import os
from flask import Flask, request, abort, jsonify
from datetime import datetime
import json
import threading
from utils.blacklist import BlacklistManager
from utils.line_bot import LineBotManager
from utils.commands import CommandHandler
from utils.admin import AdminManager
from utils.warning import WarningManager
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    JoinEvent,
    LeaveEvent,
    MemberJoinedEvent,
    MemberLeftEvent
)
from dotenv import load_dotenv
import sys

# 載入環境變數
load_dotenv()

# 檢查必要的環境變數
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("錯誤：環境變數未設定正確")
    print("請確認您已經：")
    print("1. 在專案根目錄建立 .env 檔案")
    print("2. 在 .env 檔案中設定以下變數：")
    print("   LINE_CHANNEL_ACCESS_TOKEN=你的Channel存取權杖")
    print("   LINE_CHANNEL_SECRET=你的Channel密鑰")
    print("\n目前的設定值：")
    print(f"LINE_CHANNEL_ACCESS_TOKEN: {'已設定' if CHANNEL_ACCESS_TOKEN else '未設定'}")
    print(f"LINE_CHANNEL_SECRET: {'已設定' if CHANNEL_SECRET else '未設定'}")
    sys.exit(1)

app = Flask(__name__)

# 初始化各個管理器
line_bot = LineBotManager(CHANNEL_ACCESS_TOKEN)
webhook_handler = WebhookHandler(CHANNEL_SECRET)
blacklist_manager = BlacklistManager()
admin_manager = AdminManager()
warning_manager = WarningManager(blacklist_manager)
command_handler = CommandHandler(line_bot, blacklist_manager, admin_manager, warning_manager)

def handle_violation(group_id: str, user_id: str, violation_type: str, details: str):
    """處理違規行為"""
    # 加入黑名單
    blacklist_manager.add_to_blacklist(user_id, f"違規行為: {violation_type}", None)
    
    # 發送警告通知
    message = f"""
🚫 發現違規行為
違規者ID: {user_id}
違規類型: {violation_type}
詳細資訊: {details}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
已自動加入黑名單並踢出群組
"""
    line_bot.send_alert(group_id, message)
    
    # 踢出用戶
    line_bot.kick_user(group_id, user_id)

@app.route("/")
def home():
    """首頁"""
    return jsonify({
        'status': 'ok',
        'message': 'LINE Bot Server is running',
        'endpoints': {
            '/callback': 'LINE Webhook endpoint',
            '/status': 'Server status endpoint'
        }
    })

@app.route("/callback", methods=['POST'])
def callback():
    """LINE Bot Webhook 回調"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        webhook_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@webhook_handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """處理文字訊息"""
    text = event.message.text
    user_id = event.source.user_id
    
    # 檢查是否在黑名單中
    if blacklist_manager.is_blacklisted(user_id):
        return
    
    # 處理指令
    if text.startswith('!'):
        command_handler.handle_command(event)

@webhook_handler.add(JoinEvent)
def handle_join(event):
    """處理機器人被加入群組事件"""
    group_id = event.source.group_id
    user_id = event.source.user_id
    
    # 將邀請機器人的人設為管理員
    admin_manager.initialize_group(group_id, user_id)
    
    welcome_message = """
👋 大家好！我是群組管理機器人
我可以幫助大家：
- 監控群組活動
- 管理黑名單
- 警告系統
- 踢出違規用戶

輸入 !help 查看更多功能
"""
    line_bot.send_message(group_id, welcome_message)

@webhook_handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    """處理新成員加入事件"""
    group_id = event.source.group_id
    for member in event.joined.members:
        # 檢查是否在黑名單中
        if blacklist_manager.is_blacklisted(member.user_id):
            profile = line_bot.get_group_member_profile(group_id, member.user_id)
            handle_violation(
                group_id,
                member.user_id,
                "黑名單成員加入",
                f"用戶名稱: {profile['display_name'] if profile else '未知'}"
            )

@webhook_handler.add(MemberLeftEvent)
def handle_member_left(event):
    """處理成員離開事件"""
    group_id = event.source.group_id
    for member in event.left.members:
        line_bot.send_message(
            group_id,
            f"👋 成員 {member.user_id} 已離開群組"
        )

@app.route("/status", methods=['GET'])
def status():
    """檢查服務狀態"""
    return {
        'status': 'running',
        'blacklist_count': len(blacklist_manager.get_blacklist()),
        'timestamp': datetime.now().isoformat()
    }

def start_monitoring():
    """啟動監控"""
    try:
        # 在這裡添加監控邏輯
        pass
    except Exception as e:
        print(f"監控啟動失敗: {e}")

if __name__ == "__main__":
    # 在背景執行監控
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    
    # 啟動 Flask 應用
    app.run(debug=True) 