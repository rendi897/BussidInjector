# bot.py
import requests
import json
import os
import time
from telegram import Update, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackContext
from keep_alive import keep_alive

TOKEN = "8195321637:AAEQEZPwf25f6LLRm0zA3GX6jjmTVWePvKs"
VALIDATE_KEY_URL = "https://viperrengg.serv00.net/BUSSID/backend/validate.php"

def validate_key(key):
    payload = {"key": key}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(VALIDATE_KEY_URL, json=payload, headers=headers)
    return response.json().get("valid", False)

def login_with_device(device_id):
    url = "https://4ae9.playfabapi.com/Client/LoginWithAndroidDeviceID"
    payload = {
        "AndroidDevice": "AndroidPhone",
        "AndroidDeviceId": device_id,
        "CreateAccount": True,
        "TitleId": "4AE9"
    }
    headers = {'Content-Type': "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    if 'data' in response_data and 'SessionTicket' in response_data['data']:
        return response_data['data']['SessionTicket']
    else:
        return None

def add_rp(x_auth, value, label):
    url = "https://4ae9.playfabapi.com/Client/ExecuteCloudScript"
    payload = {
        "FunctionName": "AddRp",
        "FunctionParameter": {"addValue": value},
        "GeneratePlayStreamEvent": False,
        "RevisionSelection": "Live"
    }
    headers = {
        'Content-Type': "application/json",
        'X-Authorization': x_auth
    }
    requests.post(url, json=payload, headers=headers)
    return f"✅ Inject {label} sukses!"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Selamat datang di BUSSID Inject Bot!\n"
        "Gunakan perintah:\n"
        "/login <device_id> - Login dengan Device ID\n"
        "/inject <menu> - Pilih menu UB\n"
        "/manual_input - Input Manual UB (VIP)\n"
        "/loop_add_ub - Loop 2jt UB per detik (VIP)\n"
        "/exit - Keluar dari bot\n"
        "\nMasukkan key untuk mengakses fitur VIP dengan /key <your_key>"
    )

def set_key(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_text("❌ Harap masukkan key setelah perintah.")
        return
    
    key = context.args[0]
    if validate_key(key):
        context.user_data["vip_access"] = True
        update.message.reply_text("✅ Key valid! Akses VIP diberikan.", quote=False)
        update.message.delete()
    else:
        update.message.reply_text("❌ Key tidak valid atau sudah kadaluarsa!", quote=False)
        update.message.delete()

def inject(update: Update, context: CallbackContext) -> None:
    if "vip_access" not in context.user_data:
        update.message.reply_text("❌ Anda belum memasukkan key VIP! Gunakan /key <your_key>.")
        return

    if "session_ticket" not in context.user_data:
        update.message.reply_text("❌ Anda belum login! Gunakan /login <device_id> terlebih dahulu.")
        return

    session_ticket = context.user_data["session_ticket"]
    menu_options = {
        "1": (500000, "500k UB"),
        "2": (800000, "800k UB"),
        "3": (1000000, "1jt UB"),
        "4": (-50000000, "Kurangi 50jt UB"),
        "5": (-200000000, "Kurangi 200jt UB")
    }
    update.message.reply_text(
        "Pilih jumlah UB yang ingin diinject:\n"
        "1. 500k UB\n"
        "2. 800k UB\n"
        "3. 1jt UB\n"
        "4. Kurangi 50jt UB\n"
        "5. Kurangi 200jt UB\n"
        "6. Manual Input (VIP)\n"
        "7. Loop 2jt UB per detik (VIP)\n"
        "8. Keluar\n"
        "Masukkan pilihan (1-8):"
    )

def main():
    keep_alive()  # Menjaga bot tetap hidup
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("key", set_key))
    dp.add_handler(CommandHandler("inject", inject))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
