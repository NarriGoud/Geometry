import os
import requests
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")

# -------------------- Define lifespan context --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Telegram bot in background thread
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    yield
    # (Optional) Cleanup logic on shutdown goes here

# -------------------- FastAPI app setup --------------------
app = FastAPI(lifespan=lifespan)

@app.get("/ping")
def ping():
    return {"status": "OK"}

@app.post("/upload-jsonl")
async def upload_jsonl(file: UploadFile = File(...)):
    if not file.filename.endswith(".jsonl"):
        raise HTTPException(status_code=400, detail="Only .jsonl files are allowed.")
    try:
        save_path = f"./uploaded_files/{file.filename}"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"message": f"Received file: {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

@app.post("/runpipeline")
def run_pipeline():
    return {"message": "Pipeline triggered (placeholder response)."}

# -------------------- Telegram bot setup --------------------
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

def handle_document(update: Update, context: CallbackContext):
    document = update.message.document
    if not document.file_name.endswith(".jsonl"):
        update.message.reply_text("❌ Only .jsonl files are allowed.")
        return
    try:
        file = document.get_file()
        file_content = file.download_as_bytearray()
        files = {'file': (document.file_name, file_content)}
        response = requests.post(f"{API_URL}/upload-jsonl", files=files)
        if response.status_code == 200:
            update.message.reply_text(f"✅ File uploaded: {document.file_name}")
        else:
            update.message.reply_text(f"❌ Upload failed: {response.text}")
    except Exception as e:
        update.message.reply_text(f"🚨 Error: {e}")

def run_telegram_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("ping", ping_command))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/json"), handle_document))
    updater.start_polling()
    updater.idle()
