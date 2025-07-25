import os
import requests
import asyncio
import subprocess
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
import json
from fastapi.responses import JSONResponse
from telegram import BotCommand, Update, Document
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from dotenv import load_dotenv

# -------------------- Load Environment --------------------
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")  # Example: https://your-render-api.onrender.com
WEBHOOK_PATH = "/webhook"

bot_app = None  # Global bot app reference
WAITING_FOR_JSONL = 1

# -------------------- Lifespan --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_app
    print("🔄 Starting Telegram bot with webhook...")

    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("ping", ping_command))
    bot_app.add_handler(CommandHandler("hello", hello_command))
    bot_app.add_handler(CommandHandler("runpipeline", telegram_run_pipeline))

    # ✅ Upload flow
    upload_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("upload", upload_command)],
        states={
            WAITING_FOR_JSONL: [MessageHandler(filters.Document.ALL, handle_jsonl_upload)],
        },
        fallbacks=[CommandHandler("cancel", cancel_upload)],
    )
    bot_app.add_handler(upload_conv_handler)

    await bot_app.initialize()
    await set_bot_commands(bot_app)

    # Set webhook
    webhook_url = f"{API_URL}{WEBHOOK_PATH}"
    await bot_app.bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")

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
    data = json.loads(body.decode("utf-8"))
    update = Update.de_json(data, bot_app.bot)
    await bot_app.update_queue.put(update)
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"status": "OK"}

@app.post("/upload-jsonl")
async def upload_jsonl(file: UploadFile = File(...)):
    allowed_exts = [".jsonl", ".csv", ".txt"]
    max_size = 5 * 1024 * 1024  # 5MB

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Only .jsonl, .csv, and .txt files are allowed.")

    try:
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=413, detail="File too large. Max 5MB allowed.")

        save_path = f"./uploads/{file.filename}"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(content)

        print(f"✅ File saved: {save_path}")
        return JSONResponse(status_code=200, content={"message": f"Received file: {file.filename}"})

    except HTTPException:
        raise
    except Exception as e:
        print("❌ Failed to save file:", e)
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
    await update.message.reply_text("🤖 Hello! Use /upload to send me a `.jsonl` file.")

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: hello_command triggered")
    await update.message.reply_text("👋 Welcome to the bot!")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Bot is alive!")

async def telegram_run_pipeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("⚡ Telegram triggered main pipeline")
    # subprocess.run(["python", PIPELINE_SCRIPT_PATH], check=True)
    await update.message.reply_text("✅ Main pipeline triggered (simulated)")

# -------------------- Upload Handlers --------------------
async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🟡 /upload command received")
    await update.message.reply_text("📤 Please send your `.jsonl` file now.")
    return WAITING_FOR_JSONL

async def handle_jsonl_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: handle_jsonl_upload triggered")
    document: Document = update.message.document
    allowed_exts = [".jsonl", ".csv", ".txt"]
    max_size = 5 * 1024 * 1024  # 5MB

    ext = os.path.splitext(document.file_name)[1].lower()
    if ext not in allowed_exts:
        await update.message.reply_text("❌ Only `.jsonl`, `.csv`, and `.txt` files are allowed.")
        return WAITING_FOR_JSONL

    if document.file_size > max_size:
        await update.message.reply_text("❌ File too large. Max 5MB allowed.")
        return WAITING_FOR_JSONL

    try:
        file = await document.get_file()
        byte_data = await file.download_as_bytearray()
        files = {'file': (document.file_name, byte_data)}

        print(f"📤 Uploading file to API: {document.file_name}")
        upload_url = f"{API_URL}/upload-jsonl"
        response = requests.post(upload_url, files=files)

        if response.status_code == 200:
            await update.message.reply_text("✅ File uploaded successfully.")
        else:
            await update.message.reply_text(f"❌ Upload failed: {response.status_code} - {response.text}")

    except Exception as e:
        print("❌ Upload error:", e)
        await update.message.reply_text(f"🚨 Error uploading file: {e}")

    return ConversationHandler.END


async def cancel_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("❎ Upload cancelled.")
    await update.message.reply_text("❎ Upload cancelled.")
    return ConversationHandler.END

# -------------------- Telegram Bot Commands --------------------
async def set_bot_commands(bot_app):
    commands = [
        BotCommand(command="ping", description="Check if API is alive"),
        BotCommand(command="upload", description="Upload supported file"),
        BotCommand(command="runpipeline", description="Run main pipeline"),
        BotCommand(command="hello", description="Greet the bot"),
        BotCommand(command="dataset", description="Upload dataset to Kaggle"),
    ]
    await bot_app.bot.set_my_commands(commands)
