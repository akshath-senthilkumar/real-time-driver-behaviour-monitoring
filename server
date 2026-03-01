from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import datetime
import asyncio
import csv
import os
import time
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

drivers = {}
clients: list[WebSocket] = []
LOG_FILE = "violations_log.csv"


# ─────────────────────────────────────────────
# WebSocket — Dashboard connection
# ─────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    print(f"[WS] Dashboard connected. Total: {len(clients)}")
    try:
        # Send current state immediately on connect
        await websocket.send_json(drivers)
        while True:
            await asyncio.sleep(1)
    except (WebSocketDisconnect, Exception):
        if websocket in clients:
            clients.remove(websocket)
        print(f"[WS] Dashboard disconnected. Total: {len(clients)}")


# ─────────────────────────────────────────────
# Violation endpoint — receives from driver app
# ─────────────────────────────────────────────
@app.post("/violation")
async def receive_violation(data: dict):
    driver_id = data.get("driver_id", "Unknown")
    violation = data.get("type", "none")
    duration = data.get("duration", 0)
    status = data.get("status", "safe")
    now = datetime.datetime.now()

    drivers[driver_id] = {
        "status": status,
        "violation": violation,
        "duration": duration,
        "last_seen": time.time(),
        "time": str(now.strftime("%H:%M:%S")),
        "date": str(now.strftime("%Y-%m-%d")),
    }

    # ── CSV logging (only log non-safe events) ──
    if status != "safe":
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Driver", "Violation", "Duration", "Status", "Time"])
            writer.writerow([driver_id, violation, duration, status, str(now)])

    # ── Broadcast to all dashboard clients ──
    dead_clients = []
    for client in clients:
        try:
            await client.send_json(drivers)
        except Exception:
            dead_clients.append(client)

    for c in dead_clients:
        if c in clients:
            clients.remove(c)

    return {"message": "Received", "drivers_online": len(drivers)}


# ─────────────────────────────────────────────
# Get all drivers — REST fallback for dashboard
# ─────────────────────────────────────────────
@app.get("/drivers")
async def get_drivers():
    return drivers


# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "running", "drivers": list(drivers.keys())}
