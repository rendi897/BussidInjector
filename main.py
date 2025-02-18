import threading
import time
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
import requests
import json

TOKEN = "8195321637:AAEQEZPwf25f6LLRm0zA3GX6jjmTVWePvKs"
stop_loop_event = threading.Event()

async def login_with_device(update: Update, context: CallbackContext):
    await update.message.reply_text("Masukkan Device ID Anda:")
    context.user_data['awaiting_device_id'] = True

async def process_device_id(update: Update, context: CallbackContext):
    if context.user_data.get('awaiting_device_id'):
        device_id = update.message.text
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
            context.user_data['session_ticket'] = response_data['data']['SessionTicket']
            await update.message.reply_text("Login berhasil! Gunakan /menu untuk mulai.")
        else:
            await update.message.reply_text("Login gagal! Periksa Device ID Anda.")
        
        context.user_data['awaiting_device_id'] = False

async def add_rp(update: Update, context: CallbackContext, value: int):
    if 'session_ticket' not in context.user_data:
        await update.message.reply_text("Anda harus login terlebih dahulu. Gunakan /login")
        return
    
    session_ticket = context.user_data['session_ticket']
    url = "https://4ae9.playfabapi.com/Client/ExecuteCloudScript"
    payload = {
        "CustomTags": None,
        "FunctionName": "AddRp",
        "FunctionParameter": {"addValue": value},
        "GeneratePlayStreamEvent": False,
        "RevisionSelection": "Live",
        "SpecificRevision": None,
        "AuthenticationContext": None
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
        await update.message.reply_text("Anda harus login terlebih dahulu. Gunakan /login")
        return
    
    keyboard = [
        [InlineKeyboardButton("500k UB", callback_data='500000')],
        [InlineKeyboardButton("800k UB", callback_data='800000')],
        [InlineKeyboardButton("1jt UB", callback_data='1000000')],
        [InlineKeyboardButton("Kurangi 50jt UB", callback_data='-50000000')],
        [InlineKeyboardButton("Kurangi 200jt UB", callback_data='-200000000')],
        [InlineKeyboardButton("Manual Input (VIP)", callback_data='manual')],
        [InlineKeyboardButton("Keluar", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Pilih jumlah UB yang ingin diinject:", reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == "manual":
        await query.edit_message_text("Masukkan jumlah UB yang diinginkan:")
        context.user_data['awaiting_manual_input'] = True
    elif query.data == "exit":
        context.user_data.clear()
        await query.edit_message_text("Anda telah keluar. Silakan login kembali jika ingin menggunakan bot.")
    else:
        value = int(query.data)
        await add_rp(update, context, value)

async def manual_input_handler(update: Update, context: CallbackContext):
    if context.user_data.get('awaiting_manual_input'):
        try:
            value = int(update.message.text)
            await add_rp(update, context, value)
        except ValueError:
            await update.message.reply_text("Jumlah harus berupa angka!")
        finally:
            context.user_data['awaiting_manual_input'] = False

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
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_device_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manual_input_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    main()
    
