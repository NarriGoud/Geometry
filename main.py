from api.api import app

# Only needed if testing locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.api:app", host="0.0.0.0", port=10000, reload=True)
