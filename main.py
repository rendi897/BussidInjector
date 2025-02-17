import threading
import time
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import requests
import json

TOKEN = "8195321637:AAEQEZPwf25f6LLRm0zA3GX6jjmTVWePvKs"
stop_loop_event = threading.Event()

def validate_key(key):
    url = "https://viperrengg.serv00.net/BUSSID/backend/validate.php"
    payload = {"key": key}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("valid", False)

async def login_with_device(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Gunakan format: /login <device_id>")
        return
    
    device_id = context.args[0]
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
        session_ticket = response_data['data']['SessionTicket']
        context.user_data['session_ticket'] = session_ticket
        await update.message.reply_text("Login berhasil! Gunakan /menu untuk mulai.")
    else:
        await update.message.reply_text("Login gagal! Periksa Device ID Anda.")

async def add_rp(update: Update, context: CallbackContext):
    if 'session_ticket' not in context.user_data:
        await update.message.reply_text("Anda harus login terlebih dahulu. Gunakan /login <device_id>.")
        return
    
    if not context.args:
        await update.message.reply_text("Gunakan format: /manual <jumlah>")
        return
    
    try:
        value = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Jumlah harus berupa angka!")
        return
    
    session_ticket = context.user_data['session_ticket']
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
        await update.message.reply_text(f"Inject {value} UB berhasil!")
    else:
        await update.message.reply_text("Inject gagal, coba lagi nanti.")

async def menu(update: Update, context: CallbackContext):
    if 'session_ticket' not in context.user_data:
        await update.message.reply_text("Anda harus login terlebih dahulu. Gunakan /login <device_id>.")
        return
    
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
    
    if 'session_ticket' not in context.user_data:
        await query.edit_message_text("Anda harus login terlebih dahulu. Gunakan /login <device_id>.")
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
        await add_rp(update, context)
    elif query.data == "6":
        await query.edit_message_text("Gunakan perintah /manual <jumlah> untuk input manual (VIP).")
    elif query.data == "8":
        context.user_data.clear()
        await query.edit_message_text("Anda telah keluar. Silakan login kembali jika ingin menggunakan bot.")
    elif query.data == "9":
        stop_loop_event.set()
        await query.edit_message_text("Loop 2jt UB per detik dihentikan!")
    else:
        await query.edit_message_text("Pilihan tidak valid.")

flask_app = Flask(__name__)

@flask_app.route("/")
def health_check():
    return "OK", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CommandHandler("login", login_with_device))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("manual", add_rp))
    app.add_handler(CallbackQueryHandler(button))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    main()
