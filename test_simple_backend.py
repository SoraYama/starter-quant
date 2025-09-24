#!/usr/bin/env python3
"""
简化的后端测试
"""

from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    print("Starting simple backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
