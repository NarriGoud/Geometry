import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")

# /ping command
def ping_command(update: Update, context: CallbackContext):
    try:
        response = requests.get(f"{API_URL}/ping")
        if response.status_code == 200:
            data = response.json()
            update.message.reply_text(f"📊 Status: {data.get('status', 'unknown')}")
        else:
            update.message.reply_text(f"❌ API not responding (status code: {response.status_code})")
    except Exception as e:
        update.message.reply_text(f"🚨 Error: {e}")

# Handle .jsonl file uploads
def handle_document(update: Update, context: CallbackContext):
    document = update.message.document

    # Check if it's a .jsonl file
    if not document.file_name.endswith(".jsonl"):
        update.message.reply_text("❌ Only .jsonl files are allowed.")
        return

    try:
        file = document.get_file()
        file_content = file.download_as_bytearray()

        # Upload to API
        files = {'file': (document.file_name, file_content)}
        response = requests.post(f"{API_URL}/upload-jsonl", files=files)

        if response.status_code == 200:
            update.message.reply_text(f"✅ File uploaded: {document.file_name}")
        else:
            update.message.reply_text(f"❌ Upload failed: {response.text}")
    except Exception as e:
        update.message.reply_text(f"🚨 Error: {e}")

# Start bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands and message handlers
    dp.add_handler(CommandHandler("ping", ping_command))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/json"), handle_document))

    print("[🤖] Telegram bot is listening...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
