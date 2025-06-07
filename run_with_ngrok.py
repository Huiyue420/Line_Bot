from pyngrok import ngrok, conf
from app import app
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定 ngrok authtoken
NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')
if not NGROK_AUTH_TOKEN:
    print("錯誤：未設定 NGROK_AUTH_TOKEN")
    print("請在 .env 檔案中加入：")
    print("NGROK_AUTH_TOKEN=你的_ngrok_authtoken")
    print("\n取得 authtoken 步驟：")
    print("1. 註冊 ngrok 帳號：https://dashboard.ngrok.com/signup")
    print("2. 登入後前往：https://dashboard.ngrok.com/get-started/your-authtoken")
    print("3. 複製 authtoken 並加入 .env 檔案")
    exit(1)

# 設定 ngrok
conf.get_default().auth_token = NGROK_AUTH_TOKEN

# 啟動 ngrok
try:
    http_tunnel = ngrok.connect(5000)
    public_url = http_tunnel.public_url
    print(f'\n=== ngrok 通道已開啟 ===')
    print(f'Public URL: {public_url}')
    print(f'Webhook URL: {public_url}/callback')
    print('請將 Webhook URL 設定到 LINE Developers Console 中')
    print('注意：每次重新啟動 ngrok，網址都會改變\n')
except Exception as e:
    print(f"啟動 ngrok 時發生錯誤：{str(e)}")
    exit(1)

# 啟動 Flask
app.run() 