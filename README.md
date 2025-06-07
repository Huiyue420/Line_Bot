# LINE 群組管理機器人

這是一個基於 LINE Official Account 的群組管理機器人，提供群組監控、黑名單管理、警告系統等功能。

## 功能特點

- 群組成員監控
- 黑名單系統
- 警告系統（三振出局）
- 管理員權限管理
- 自動踢出違規用戶
- 群組事件記錄
- 管理員指令系統

## 系統需求

- Python 3.8+
- Flask
- LINE Official Account（免費版即可）
- 可公開訪問的伺服器（用於接收 Webhook）

## 安裝步驟

1. 克隆專案：
```bash
git clone https://github.com/Huiyue420/Line_Bot.git
cd line_bot
```

2. 建立虛擬環境：
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安裝依賴：
```bash
pip install -r requirements.txt
```

4. 設定環境變數：
   - 在專案根目錄建立 `.env` 文件
   - 填入以下內容：
```
LINE_CHANNEL_ACCESS_TOKEN=你的Channel存取權杖
LINE_CHANNEL_SECRET=你的Channel密鑰
NGROK_AUTH_TOKEN=你的ngrok_authtoken
```

   - 取得 ngrok authtoken：
     1. 註冊 [ngrok 帳號](https://dashboard.ngrok.com/signup)
     2. 登入後前往 [authtoken 頁面](https://dashboard.ngrok.com/get-started/your-authtoken)
     3. 複製 authtoken 並填入 `.env` 檔案

## LINE Official Account 設置

1. 申請 LINE 官方帳號：
   - 前往 [LINE Official Account](https://www.linebiz.com/tw/service/line-official-account/)
   - 選擇免費方案
   - 完成基本設定

2. 開啟 Messaging API：
   - 登入 [LINE Developers Console](https://developers.line.biz/console/)
   - 建立 Provider（如果沒有）
   - 選擇您的官方帳號
   - 在 Messaging API 設定中：
     * 生成 Channel access token
     * 記下 Channel secret
     * 設定 Webhook URL（開發時會由 ngrok 提供）

3. 設定 Webhook（重要）：
   - 在 LINE Developers Console 中：
     * 選擇你的 Provider
     * 點擊你的 LINE Official Account Channel
     * 在左側選單找到「Messaging API」設定
   - 在「Webhook settings」區塊：
     * 填入 Webhook URL：`https://你的網域/callback`
     * 如果使用 ngrok：`https://xxxx-xxx-xxx-xxx-xxx.ngrok.io/callback`
     * 點擊「Update」儲存 URL
     * 將「Use webhook」設定為「Enabled」（開啟）
     * 可以點擊「Verify」測試連線
   - 在「Response settings」區塊：
     * 關閉「Auto-reply messages」（重要！）
     * 關閉「Greeting messages」（重要！）
     * 將「Chat」功能設為「Disabled」

4. 確認設定：
   - Webhook URL 已正確填入並更新
   - Webhook 功能已啟用
   - 自動回覆訊息已關閉
   - 伺服器正在運行
   - 使用 `!help` 指令測試機器人

注意：如果沒有正確設定 Webhook 或關閉自動回覆，機器人會：
- 無法接收或處理群組訊息
- 只會發送預設的自動回覆訊息
- 無法執行任何指令

## 開發環境設置

1. 使用 ngrok 進行本地開發：
   - 確保已經設定好 `.env` 檔案中的 `NGROK_AUTH_TOKEN`
   - 如果沒有看到通道建立成功的訊息，請檢查：
     * `.env` 檔案是否存在
     * `NGROK_AUTH_TOKEN` 是否正確
     * 是否已經啟動虛擬環境
```bash
# 啟動帶有 ngrok 的開發伺服器
python run_with_ngrok.py
```
   - 成功時會顯示：
     * Public URL（公開網址）
     * Webhook URL（LINE Bot 設定用的網址）
   - 將 Webhook URL 設定到 LINE Developers Console
   - 注意：每次重新啟動 ngrok，網址都會改變

2. 直接啟動（需要可公開訪問的網址）：
```bash
python app.py
```

## 部署說明

1. 本地開發：
   - 使用 `run_with_ngrok.py` 啟動，會自動提供臨時的公開網址
   - 適合開發和測試階段

2. 正式部署：
   - 需要一個可公開訪問的伺服器
   - 建議使用：
     * Heroku
     * Railway
     * GCP
     * Azure
   - 使用 `gunicorn` 作為生產環境伺服器：
```bash
gunicorn app:app
```

## 使用方法

1. 加入機器人為好友：
   - 掃描您的 LINE 官方帳號 QR Code
   - 加入為好友

2. 邀請機器人到群組：
   - 在群組中選擇「邀請」
   - 選擇您的官方帳號
   - 邀請者會自動成為該群組的第一位管理員

3. 一般指令：
   - `!help` - 顯示幫助訊息
   - `!status` - 查看機器人狀態
   - `!report [@用戶] [原因]` - 回報違規用戶

4. 管理員指令：
   - `!admin list` - 查看管理員列表
   - `!admin add [@用戶]` - 新增管理員
   - `!admin remove [@用戶]` - 移除管理員
   - `!blacklist` - 查看黑名單
   - `!warn [@用戶] [原因]` - 對用戶發出警告
   - `!unwarn [@用戶]` - 移除用戶警告
   - `!warnings [@用戶]` - 查看用戶警告記錄
   - `!kick [@用戶] [原因]` - 將用戶踢出群組

5. 自動功能：
   - 警告累計 3 次自動踢出並加入黑名單
   - 被踢出的用戶自動加入黑名單
   - 黑名單用戶嘗試加入群組時自動踢出
   - 自動保護管理員不被踢出

## 專案結構

```
line_bot/
├── app.py              # 主應用程式
├── run_with_ngrok.py   # 開發環境啟動腳本
├── requirements.txt    # 相依套件
├── .env               # 環境變數（請自行建立）
├── .gitignore         # Git 忽略檔案
├── data/              # 資料儲存目錄
│   ├── admins.json    # 管理員資料
│   ├── warnings.json  # 警告記錄
│   └── blacklist.json # 黑名單資料
└── utils/
    ├── admin.py       # 管理員權限管理
    ├── warning.py     # 警告系統
    ├── line_bot.py    # LINE Bot 管理模組
    └── blacklist.py   # 黑名單管理模組
```

## 注意事項

1. 免費版限制：
   - 每月訊息則數上限：500 則
   - 好友數上限：500 個
   - API 呼叫限制：
     * Push Message：每分鐘 500 次
     * Reply Message：每分鐘 1000 次
     * Multicast：每次最多 150 個接收者

2. 開發注意事項：
   - 不要將 `.env` 檔案上傳到 Git
   - 定期備份 data 目錄下的資料
   - 使用 `ngrok` 時，每次重啟都會得到新的 URL
   - 正式部署時建議使用固定網址

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

## 授權條款

MIT License