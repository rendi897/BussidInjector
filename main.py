from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import requests
import json
import os

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
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    if response.status_code == 200 and 'data' in response_data and 'SessionTicket' in response_data['data']:
        return response_data['data']['SessionTicket']
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
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return f"Inject {label} berhasil!"
    return "Inject gagal, coba lagi nanti."

# Fungsi perintah /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Selamat datang di BUSSID Inject Bot! Kirim /login <device_id> untuk login.")

# Fungsi perintah /login
async def login(update: Update, context: CallbackContext):
    args = update.message.text.split()[1:]  # Ambil argumen setelah command
    if len(args) != 1:
        await update.message.reply_text("Gunakan format: /login <device_id>")
        return

    device_id = args[0]
    session_ticket = login_with_device(device_id)

    if session_ticket:
        context.user_data['session_ticket'] = session_ticket
        await update.message.reply_text("Login berhasil! Gunakan /inject <jumlah> untuk inject UB.")
    else:
        await update.message.reply_text("Login gagal. Coba lagi dengan Device ID yang benar.")

# Fungsi perintah /inject
async def inject(update: Update, context: CallbackContext):
    if 'session_ticket' not in context.user_data:
        await update.message.reply_text("Anda belum login. Gunakan /login <device_id>")
        return

    args = update.message.text.split()[1:]  # Ambil argumen setelah command
    if len(args) != 1 or not args[0].isdigit():
        await update.message.reply_text("Gunakan format: /inject <jumlah_UB>")
        return

    ub_value = int(args[0])
    result = add_rp(context.user_data['session_ticket'], ub_value, f"{ub_value} UB")
    await update.message.reply_text(result)

# Konfigurasi bot Telegram
def main():
    app = Application.builder().token(TOKEN).build()

    # Tambahkan handler ke bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("inject", inject))

    # Jalankan bot dengan polling
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
