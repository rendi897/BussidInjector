from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import requests
import json
import os
import time

TOKEN = "8195321637:AAEQEZPwf25f6LLRm0zA3GX6jjmTVWePvKs"

# Fungsi untuk validasi key
def validate_key(key):
    url = "https://viperrengg.serv00.net/BUSSID/backend/validate.php"
    payload = {"key": key}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("valid", False)

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

# Fungsi untuk menampilkan menu inline button
async def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("500k UB", callback_data='1')],
        [InlineKeyboardButton("800k UB", callback_data='2')],
        [InlineKeyboardButton("1jt UB", callback_data='3')],
        [InlineKeyboardButton("Kurangi 50jt UB", callback_data='4')],
        [InlineKeyboardButton("Kurangi 200jt UB", callback_data='5')],
        [InlineKeyboardButton("Manual Input (VIP)", callback_data='6')],
        [InlineKeyboardButton("Loop 2jt UB per detik (VIP)", callback_data='7')],
        [InlineKeyboardButton("Keluar", callback_data='8')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Pilih jumlah UB yang ingin diinject:", reply_markup=reply_markup)

# Fungsi untuk menangani tombol inline
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    ub_values = {
        "1": (500000, "500k UB"),
        "2": (800000, "800k UB"),
        "3": (1000000, "1jt UB"),
        "4": (-50000000, "Kurangi 50jt UB"),
        "5": (-200000000, "Kurangi 200jt UB")
    }

    if query.data in ub_values:
        rp_value, label = ub_values[query.data]
        result = add_rp(context.user_data.get('session_ticket', ''), rp_value, label)
        await query.edit_message_text(result)
    elif query.data == "6":
        await query.edit_message_text("Gunakan perintah /manual <jumlah> untuk input manual (VIP).")
    elif query.data == "7":
        await query.edit_message_text("Loop 2jt UB per detik belum didukung di bot ini.")
    elif query.data == "8":
        await query.edit_message_text("Keluar dari program.")
    else:
        await query.edit_message_text("Pilihan tidak valid.")

# Fungsi perintah /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Selamat datang di BUSSID Inject Bot! Kirim /login <device_id> untuk login.")

# Fungsi perintah /login
async def login(update: Update, context: CallbackContext):
    args = update.message.text.split()[1:]
    if len(args) != 1:
        await update.message.reply_text("Gunakan format: /login <device_id>")
        return

    device_id = args[0]
    session_ticket = login_with_device(device_id)

    if session_ticket:
        context.user_data['session_ticket'] = session_ticket
        await update.message.reply_text("Login berhasil! Gunakan /menu untuk melihat pilihan inject UB.")
    else:
        await update.message.reply_text("Login gagal. Coba lagi dengan Device ID yang benar.")

# Konfigurasi bot Telegram
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button))
    
    print("Bot is running...")
    app.run_polling()

# Flask untuk Health Check
flask_app = Flask(__name__)

@flask_app.route("/")
def health_check():
    return "OK", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    main()
