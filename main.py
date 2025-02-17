import threading
import time
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import requests
import json
import os

TOKEN = "8195321637:AAEQEZPwf25f6LLRm0zA3GX6jjmTVWePvKs"

stop_loop_event = threading.Event()

def validate_key(key):
    url = "https://viperrengg.serv00.net/BUSSID/backend/validate.php"
    payload = {"key": key}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
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

    if response.status_code == 200 and 'data' in response_data and 'SessionTicket' in response_data['data']:
        return response_data['data']['SessionTicket']
    return None

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
    return f"Inject {label} berhasil!" if response.status_code == 200 else "Inject gagal, coba lagi nanti."

def loop_2jt_per_detik(session_ticket):
    while not stop_loop_event.is_set():
        result = add_rp(session_ticket, 2000000, "2jt UB")
        print(result)
        time.sleep(1)
    print("Loop dihentikan.")

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Selamat datang di BUSSID Inject Bot! Kirim /login <device_id> untuk login.")

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

async def set_key(update: Update, context: CallbackContext):
    args = update.message.text.split()[1:]
    if len(args) != 1:
        await update.message.reply_text("Gunakan format: /key <key>")
        return

    key = args[0]
    if validate_key(key):
        context.user_data['key_valid'] = True
        await update.message.reply_text("Key valid! Sekarang Anda dapat mengakses menu Loop 2jt dan Manual Input.")
    else:
        context.user_data['key_valid'] = False
        await update.message.reply_text("Key tidak valid! Coba lagi dengan key yang benar.")

async def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("500k UB", callback_data='1')],
        [InlineKeyboardButton("800k UB", callback_data='2')],
        [InlineKeyboardButton("1jt UB", callback_data='3')],
        [InlineKeyboardButton("Kurangi 50jt UB", callback_data='4')],
        [InlineKeyboardButton("Kurangi 200jt UB", callback_data='5')],
        [InlineKeyboardButton("Manual Input (VIP)", callback_data='6')],
        [InlineKeyboardButton("Loop 2jt UB per detik (VIP)", callback_data='7')],
        [InlineKeyboardButton("Stop Loop", callback_data='9')],
        [InlineKeyboardButton("Keluar", callback_data='8')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Pilih jumlah UB yang ingin diinject:", reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == "9":
        stop_loop_event.set()
        await query.edit_message_text("Loop 2jt UB per detik dihentikan!")
        return
    
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
    elif query.data == "8":
        stop_loop_event.set()
        context.user_data.clear()
        await query.edit_message_text("Anda telah keluar. Silakan login kembali jika ingin menggunakan bot.")

flask_app = Flask(__name__)

@flask_app.route("/")
def health_check():
    return "OK", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("key", set_key))
    app.add_handler(CallbackQueryHandler(button))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    main()
    
