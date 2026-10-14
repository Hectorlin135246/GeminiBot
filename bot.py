import os
import time
import requests
from google import genai

# 從 Render 雲端環境變數讀取（安全作法）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

client = genai.Client(api_key=GEMINI_API_KEY)
TG_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_tg_message(chat_id, text):
    url = f"{TG_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"發送 Telegram 訊息失敗: {e}")

def ask_gemini(prompt):
    models_to_try = ['gemini-3.8-flash', 'gemini-2.0-flash']
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"⚠️ [{model_name}] 嘗試失敗: {e}")
            time.sleep(1)
    return "🤖 Gemini 伺服器目前較繁忙，請稍後再試！"

def main():
    print("🚀 雲端 Telegram Gemini 機器人啟動成功，監聽中...")
    offset = -1
    while True:
        try:
            url = f"{TG_API_URL}/getUpdates?offset={offset}&timeout=20"
            res = requests.get(url, timeout=25).json()
            if res.get("ok"):
                for result in res.get("result", []):
                    offset = result["update_id"] + 1
                    msg = result.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    user_text = msg.get("text", "")
                    
                    if chat_id and user_text:
                        print(f"\n[收到訊息]: {user_text}")
                        if user_text == "/start":
                            send_tg_message(chat_id, "👋 你好！我是你的 Gemini AI 助手，請直接輸入問題問我喔！")
                        else:
                            reply = ask_gemini(user_text)
                            send_tg_message(chat_id, reply)
                            print(f"✨ 回覆完成！")
        except Exception as e:
            time.sleep(2)

if __name__ == '__main__':
    main()