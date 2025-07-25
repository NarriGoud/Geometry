from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is running"}

@app.get("/ping")
def ping():
    return {"status": "ok"}

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"status": "OK"}

@app.post("/upload-jsonl")
async def upload_jsonl(file: UploadFile = File(...)):
    if not file.filename.endswith(".jsonl"):
        raise HTTPException(status_code=400, detail="Only .jsonl files are allowed.")

    try:
        # Save uploaded file to disk (optional — you can change this path)
        save_path = f"./uploaded_files/{file.filename}"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)

        return {"message": f"Received file: {file.filename}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

@app.post("/runpipeline")
async def run_pipeline():
    # Dummy placeholder for triggering your ML pipeline
    return {"message": "Pipeline triggered (placeholder response)."}

@app.get("/get-logs")
async def get_logs():
    # Dummy response — later, return logs from storage or file
    return {"logs": ["[INFO] Dummy log entry 1", "[INFO] Dummy log entry 2"]}

@app.get("/status")
async def get_status():
    # Placeholder for future system/queue/model status
    return {"model_status": "idle", "last_run": "not yet triggered"}
