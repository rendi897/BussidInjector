from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import json
import os
import time

TOKEN = "8195321637:AAEQEZPwf25f6LLRm0zA3GX6jjmTVWePvKs"

# Fungsi untuk login dengan Device ID
def login_with_device(device_id):
    url = "https://4ae9.playfabapi.com/Client/LoginWithAndroidDeviceID"
    payload = {
        "AndroidDevice": "AndroidPhone",
        "AndroidDeviceId": device_id,
        "CreateAccount": True,
        "TitleId": "4AE9"
    }
    headers = {'Content-Type': "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response_data = response.json()
    
    if 'data' in response_data and 'SessionTicket' in response_data['data']:
        return response_data['data']['SessionTicket']
    else:
        return None

# Fungsi untuk menambahkan UB
def add_rp(session_ticket, value, label):
    url = "https://4ae9.playfabapi.com/Client/ExecuteCloudScript"
    payload = {
        "FunctionName": "AddRp",
        "FunctionParameter": {"addValue": value},
        "GeneratePlayStreamEvent": False,
        "RevisionSelection": "Live"
    }
    headers = {
        'Content-Type': "application/json",
        'X-Authorization': session_ticket
    }
    requests.post(url, data=json.dumps(payload), headers=headers)
    return f"Inject {label} berhasil!"

# Fungsi perintah /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Selamat datang di BUSSID Inject Bot! Kirim /login <device_id> untuk login.")

# Fungsi perintah /login
def login(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Gunakan format: /login <device_id>")
        return
    
    device_id = context.args[0]
    session_ticket = login_with_device(device_id)
    
    if session_ticket:
        context.user_data['session_ticket'] = session_ticket
        update.message.reply_text("Login berhasil! Gunakan /inject <jumlah> untuk inject UB.")
    else:
        update.message.reply_text("Login gagal. Coba lagi dengan Device ID yang benar.")

# Fungsi perintah /inject
def inject(update: Update, context: CallbackContext):
    if 'session_ticket' not in context.user_data:
        update.message.reply_text("Anda belum login. Gunakan /login <device_id>")
        return
    
    if len(context.args) != 1 or not context.args[0].isdigit():
        update.message.reply_text("Gunakan format: /inject <jumlah_UB>")
        return
    
    ub_value = int(context.args[0])
    result = add_rp(context.user_data['session_ticket'], ub_value, f"{ub_value} UB")
    update.message.reply_text(result)

# Konfigurasi bot Telegram
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("inject", inject))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
