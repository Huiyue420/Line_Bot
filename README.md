# LINE 群組管理機器人

這是一個用於管理 LINE 群組的自動化機器人，主要功能包括：
- 自動監控群組操作變更
- 管理黑名單用戶
- 自動踢除非法操作的用戶
- 追蹤並處理邀請者

## 專案結構
```
project/
├── app.py                  # 主要的 LINE Bot 應用程式
├── observer.py             # 群組觀察者模組（監控群組變更）
├── utils/
│   └── blacklist.py        # 黑名單管理模組
├── logs/                   # 事件日誌資料夾
│   └── *.json             # 各群組的事件記錄
├── venv/                   # Python 虛擬環境
├── blacklist.json         # 黑名單資料
├── requirements.txt       # 相依套件清單
└── README.md             # 專案說明文件
```

## 環境需求
- Python 3.8+
- Flask
- LINE Messaging API SDK
- 其他相依套件（詳見 requirements.txt）

## 安裝步驟

### 1. 建立虛擬環境
```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate
```

### 2. 安裝相依套件
```bash
pip install -r requirements.txt
```

### 3. 設定環境變數
建立 `.env` 檔案並填入以下資訊：
```
LINE_CHANNEL_ACCESS_TOKEN=你的頻道存取權杖
LINE_CHANNEL_SECRET=你的頻道密鑰
LINE_OBSERVER_ACCOUNT=觀察者帳號
LINE_OBSERVER_PASSWORD=觀察者密碼
ADMIN_IDS=管理員1,管理員2
TARGET_GROUP_IDS=群組1,群組2

# 資料庫設定（如果使用 MongoDB）
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=line_bot_db
```

### 4. LINE Developer 設定
1. 在 [LINE Developers Console](https://developers.line.biz/console/) 建立新的 Provider
2. 建立一個 Messaging API Channel
3. 取得 Channel Secret 和 Channel Access Token
4. 設定 Webhook URL：`https://你的網域/callback`
5. 開啟 Webhook 接收功能

## 功能說明

### 1. 群組監控功能（observer.py）
- 使用混合式架構（官方 API + 非官方客戶端）監控群組
- 自動偵測：
  - 成員變動（誰被踢出）
  - 相簿變更
  - 公告變更
- 自動記錄所有變更到 logs/ 目錄

### 2. 黑名單管理（utils/blacklist.py）
- 完整的黑名單管理系統
- 記錄所有操作歷史
- 自動踢出黑名單用戶
- 支援黑名單的匯入/匯出

### 3. 管理員指令
在群組中可使用以下指令（需要管理員權限）：
- `!黑名單`：查看黑名單列表
- `!封鎖 <user_id>`：將用戶加入黑名單
- `!解除 <user_id>`：從黑名單移除用戶
- `!歷史記錄`：查看最近的操作記錄

## 注意事項

### 安全性考慮
1. 妥善保管以下敏感資訊：
   - Channel Secret
   - Channel Access Token
   - 觀察者帳號密碼
2. 建議使用小號作為觀察者帳號
3. 定期備份黑名單和記錄檔

### 使用限制
1. 機器人需要群組管理員權限
2. 觀察者帳號需要加入目標群組
3. 建議部署到有固定 IP 的伺服器
4. 使用非官方客戶端可能有被 LINE 封鎖的風險

## 開發進度

### 已完成功能
- [x] 基本的 LINE Bot 框架
- [x] 黑名單管理系統
- [x] 群組監控模組
- [x] 管理員指令介面
- [x] 事件記錄系統

### 進行中
- [ ] 資料庫整合（目前使用 JSON 檔案）
- [ ] 管理員網頁介面
- [ ] 自訂回應訊息
- [ ] 群組設定備份功能

## 貢獻指南
1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 發送 Pull Request

## 授權
待定

## 更新日誌

### [0.1.0] - 2024-03-XX
- 初始版本
- 基本功能實作
- 文件建立 