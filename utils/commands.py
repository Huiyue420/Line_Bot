from typing import Dict, Callable, List, Optional
from datetime import datetime

class CommandHandler:
    def __init__(self, line_bot, blacklist_manager, admin_manager, warning_manager):
        self.line_bot = line_bot
        self.blacklist_manager = blacklist_manager
        self.admin_manager = admin_manager
        self.warning_manager = warning_manager
        self.commands: Dict[str, Callable] = {
            # 一般指令
            '!help': self.cmd_help,
            '!status': self.cmd_status,
            '!report': self.cmd_report,
            
            # 管理員指令
            '!admin': self.cmd_admin,
            '!blacklist': self.cmd_blacklist,
            '!warn': self.cmd_warn,
            '!unwarn': self.cmd_unwarn,
            '!kick': self.cmd_kick,
            '!warnings': self.cmd_warnings
        }

    def handle_command(self, event) -> None:
        """處理指令"""
        text = event.message.text.split()
        command = text[0].lower()
        args = text[1:] if len(text) > 1 else []

        if command not in self.commands:
            self.line_bot.send_message(
                event.source.group_id,
                "❌ 未知的指令。輸入 !help 查看可用指令。"
            )
            return

        # 檢查管理員權限
        admin_commands = {'!admin', '!blacklist', '!warn', '!unwarn', '!kick'}
        if command in admin_commands:
            if not self.admin_manager.is_admin(event.source.group_id, event.source.user_id):
                self.line_bot.send_message(
                    event.source.group_id,
                    "❌ 權限不足。此指令僅限管理員使用。"
                )
                return

        # 執行指令
        self.commands[command](event, args)

    def cmd_warnings(self, event, args) -> None:
        """查看用戶警告"""
        if not args:
            self.line_bot.send_message(
                event.source.group_id,
                "❌ 使用方式：!warnings [@用戶]"
            )
            return

        user_id = args[0]
        warnings = self.warning_manager.get_warnings(event.source.group_id, user_id)
        
        if not warnings:
            self.line_bot.send_message(
                event.source.group_id,
                f"✅ {user_id} 目前沒有警告記錄"
            )
            return

        message = f"""
⚠️ 警告記錄 - {user_id}
-------------------
警告次數: {len(warnings)}
"""
        for i, warning in enumerate(warnings, 1):
            message += f"\n#{i}"
            message += f"\n原因: {warning['reason']}"
            message += f"\n警告者: {warning['warned_by']}"
            message += f"\n時間: {warning['timestamp']}\n"

        self.line_bot.send_message(event.source.group_id, message)

    def cmd_help(self, event, args) -> None:
        """顯示幫助訊息"""
        is_admin = self.admin_manager.is_admin(event.source.group_id, event.source.user_id)
        
        help_message = """
📖 指令列表：

一般指令：
!help - 顯示此幫助訊息
!status - 查看機器人狀態
!report [@用戶] [原因] - 回報違規用戶
"""

        if is_admin:
            help_message += """
管理員指令：
!admin list - 查看管理員列表
!admin add [@用戶] - 新增管理員
!admin remove [@用戶] - 移除管理員
!blacklist - 查看黑名單
!warn [@用戶] [原因] - 對用戶發出警告
!unwarn [@用戶] - 移除用戶警告
!warnings [@用戶] - 查看用戶警告記錄
!kick [@用戶] [原因] - 將用戶踢出群組

注意：
- 用戶ID請使用 @ 標註
- 警告累計3次將自動加入黑名單並踢出群組
- 被踢出的用戶會自動加入黑名單
"""

        self.line_bot.send_message(event.source.group_id, help_message)

    def cmd_status(self, event, args) -> None:
        """查看機器人狀態"""
        admin_count = len(self.admin_manager.get_admins(event.source.group_id))
        status_message = f"""
ℹ️ 機器人狀態
-------------------
運行狀態: 正常
管理員數量: {admin_count}
黑名單數量: {len(self.blacklist_manager.get_blacklist())}
更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.line_bot.send_message(event.source.group_id, status_message)

    def cmd_admin(self, event, args) -> None:
        """管理員相關指令"""
        if not args:
            self.line_bot.send_message(
                event.source.group_id,
                "❌ 使用方式：\n!admin list\n!admin add [@用戶]\n!admin remove [@用戶]"
            )
            return

        sub_command = args[0].lower()
        
        if sub_command == 'list':
            admins = self.admin_manager.get_admins(event.source.group_id)
            if not admins:
                message = "👥 目前沒有管理員"
            else:
                message = "👥 管理員列表：\n"
                for admin_id in admins:
                    message += f"- {admin_id}\n"
            self.line_bot.send_message(event.source.group_id, message)
            
        elif sub_command == 'add' and len(args) > 1:
            target_user = args[1]
            if self.admin_manager.add_admin(event.source.group_id, target_user):
                self.line_bot.send_message(
                    event.source.group_id,
                    f"✅ 已新增管理員：{target_user}"
                )
            else:
                self.line_bot.send_message(
                    event.source.group_id,
                    f"❌ {target_user} 已經是管理員"
                )
                
        elif sub_command == 'remove' and len(args) > 1:
            target_user = args[1]
            if self.admin_manager.remove_admin(event.source.group_id, target_user):
                self.line_bot.send_message(
                    event.source.group_id,
                    f"✅ 已移除管理員：{target_user}"
                )
            else:
                self.line_bot.send_message(
                    event.source.group_id,
                    f"❌ {target_user} 不是管理員"
                )
        else:
            self.line_bot.send_message(
                event.source.group_id,
                "❌ 無效的子指令"
            )

    def cmd_blacklist(self, event, args) -> None:
        """查看黑名單"""
        blacklist = self.blacklist_manager.get_blacklist()
        if not blacklist:
            message = "📋 黑名單為空"
        else:
            message = "📋 黑名單列表：\n"
            for user_id, info in blacklist.items():
                message += f"\n用戶ID: {user_id}"
                message += f"\n原因: {info['reason']}"
                message += f"\n時間: {info['timestamp']}\n"
        
        self.line_bot.send_message(event.source.group_id, message)

    def cmd_report(self, event, args) -> None:
        """回報違規用戶"""
        if len(args) < 2:
            self.line_bot.send_message(
                event.source.group_id,
                "❌ 使用方式：!report [@用戶] [原因]"
            )
            return

        user_id = args[0]
        reason = ' '.join(args[1:])
        
        # 記錄違規報告
        report_message = f"""
⚠️ 違規報告
-------------------
被檢舉者: {user_id}
檢舉原因: {reason}
檢舉者: {event.source.user_id}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.line_bot.send_message(event.source.group_id, report_message)

    def cmd_warn(self, event, args) -> None:
        """警告用戶"""
        if len(args) < 2:
            self.line_bot.send_message(
                event.source.group_id,
                "❌ 使用方式：!warn [@用戶] [原因]"
            )
            return

        user_id = args[0]
        reason = ' '.join(args[1:])
        
        # 檢查是否在黑名單中
        if self.blacklist_manager.is_blacklisted(user_id):
            self.line_bot.send_message(
                event.source.group_id,
                f"❌ {user_id} 已在黑名單中"
            )
            return

        # 新增警告
        result = self.warning_manager.add_warning(
            event.source.group_id,
            user_id,
            reason,
            event.source.user_id
        )
        
        if result['status'] == 'blacklisted':
            message = f"""
⛔ 用戶已被自動加入黑名單
-------------------
用戶: {user_id}
原因: 達到最大警告次數 (3次)
最後警告原因: {reason}
執行者: {event.source.user_id}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

系統已自動將用戶踢出群組
"""
            # 踢出用戶
            self.line_bot.kick_user(event.source.group_id, user_id)
        else:
            message = f"""
⚠️ 警告通知
-------------------
警告對象: {user_id}
警告原因: {reason}
執行者: {event.source.user_id}
警告次數: {result['warning_count']}/3
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.line_bot.send_message(event.source.group_id, message)

    def cmd_unwarn(self, event, args) -> None:
        """移除警告"""
        if len(args) < 1:
            self.line_bot.send_message(
                event.source.group_id,
                "❌ 使用方式：!unwarn [@用戶]"
            )
            return

        user_id = args[0]
        if self.warning_manager.remove_warning(event.source.group_id, user_id):
            remaining_warnings = len(self.warning_manager.get_warnings(event.source.group_id, user_id))
            message = f"""
✅ 警告移除
-------------------
用戶: {user_id}
執行者: {event.source.user_id}
剩餘警告: {remaining_warnings}/3
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        else:
            message = f"❌ {user_id} 目前沒有警告記錄"
        
        self.line_bot.send_message(event.source.group_id, message)

    def cmd_kick(self, event, args) -> None:
        """踢出用戶"""
        if len(args) < 2:
            self.line_bot.send_message(
                event.source.group_id,
                "❌ 使用方式：!kick [@用戶] [原因]"
            )
            return

        user_id = args[0]
        reason = ' '.join(args[1:])
        
        # 檢查是否為管理員
        if self.admin_manager.is_admin(event.source.group_id, user_id):
            self.line_bot.send_message(
                event.source.group_id,
                "❌ 無法踢出管理員"
            )
            return
        
        # 踢出用戶
        if self.line_bot.kick_user(event.source.group_id, user_id):
            # 自動加入黑名單
            self.blacklist_manager.add_to_blacklist(
                user_id,
                f"被管理員踢出：{reason}",
                None
            )
            
            message = f"""
🚫 用戶已被踢出
-------------------
用戶: {user_id}
原因: {reason}
執行者: {event.source.user_id}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

用戶已自動加入黑名單
"""
        else:
            message = "❌ 踢出用戶失敗"
        
        self.line_bot.send_message(event.source.group_id, message) 