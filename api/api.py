import os
import requests
import asyncio
import subprocess
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from telegram import BotCommand, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from dotenv import load_dotenv
import json

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")  # e.g. https://your-render-app.onrender.com
WEBHOOK_PATH = "/webhook"

bot_app = None  # Global bot app reference

# -------------------- Lifespan --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_app
    print("🔄 Starting Telegram bot with webhook...")

    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("hello", hello_command))
    bot_app.add_handler(CommandHandler("runpipeline", telegram_run_pipeline))
    bot_app.add_handler(MessageHandler(filters.Document.ALL, handle_jsonl_upload))

    await bot_app.initialize()
    await set_bot_commands(bot_app)

    # Set webhook to your live Render API
    webhook_url = f"{API_URL}{WEBHOOK_PATH}"
    await bot_app.bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")

    # Start the bot - this runs the update queue processor so handlers actually run!
    await bot_app.start()

    start_scheduler()
    yield

    print("🔄 Stopping Telegram bot...")
    await bot_app.stop()

# -------------------- FastAPI App --------------------
app = FastAPI(lifespan=lifespan)

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    body = await request.body()
    data = json.loads(body.decode("utf-8"))  # Parse incoming JSON to dict
    update = Update.de_json(data, bot_app.bot)
    await bot_app.update_queue.put(update)
    return {"status": "ok"}

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
        print(f"✅ File saved: {save_path}")
        return {"message": f"Received file: {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

@app.post("/runpipeline")
def run_pipeline():
    print("🕒 Triggered main pipeline... [SIMULATION]")
    # subprocess.run(["python", PIPELINE_SCRIPT_PATH], check=True)
    return {"message": "Pipeline triggered successfully."}

# -------------------- Scheduler --------------------
def run_scheduled_pipeline():
    try:
        print("🕒 [Scheduled] Running main.py pipeline... [SIMULATION]")
        # subprocess.run(["python", PIPELINE_SCRIPT_PATH], check=True)
        print("✅ Scheduled job executed [SIMULATED]")
    except Exception as e:
        print("❌ [Scheduled] Pipeline failed:", e)

def start_scheduler():
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Kolkata"))
    scheduler.add_job(run_scheduled_pipeline, IntervalTrigger(minutes=3))
    scheduler.start()
    print("📅 Scheduler started to run every 3 minutes.")

# -------------------- Telegram Commands --------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: start_command triggered")
    await update.message.reply_text("🤖 Hello! Send me a `.jsonl` file to upload.")

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: hello_command triggered")
    await update.message.reply_text("Welcome to Telegram bot")

async def telegram_run_pipeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("⚡ Telegram triggered main pipeline")
    # subprocess.run(["python", PIPELINE_SCRIPT_PATH], check=True)
    await update.message.reply_text("✅ Main pipeline triggered (simulated)")

async def handle_jsonl_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: handle_jsonl_upload triggered")
    document = update.message.document
    if not document.file_name.endswith(".jsonl"):
        await update.message.reply_text("❌ Only `.jsonl` files are allowed.")
        return
    try:
        file = await document.get_file()
        byte_data = await file.download_as_bytearray()
        files = {'file': (document.file_name, byte_data)}
        print(f"📤 Uploading file to API: {document.file_name}")
        response = requests.post(f"{API_URL}/upload-jsonl", files=files)
        if response.status_code == 200:
            await update.message.reply_text(f"✅ File uploaded: {document.file_name}")
        else:
            await update.message.reply_text(f"❌ Upload failed: {response.text}")
    except Exception as e:
        print("❌ Upload error:", e)
        await update.message.reply_text(f"🚨 Error: {e}")

async def set_bot_commands(bot_app):
    commands = [
        BotCommand(command="ping", description="Check if API is alive"),
        BotCommand(command="upload", description="Upload a `.jsonl` file"),
        BotCommand(command="runpipeline", description="Trigger the model pipeline"),
        BotCommand(command="hello", description="Greet the bot"),
    ]
    await bot_app.bot.set_my_commands(commands)
