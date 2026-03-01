🚗 Real-Time Driver Behaviour Monitoring System








📌 Overview

A real-time multi-driver behaviour monitoring system that detects unsafe driving behaviours using computer vision and displays live alerts on a centralized dashboard.

The system supports concurrent drivers and performs rule-based violation detection with critical alert escalation.

🎯 Behaviours Detected

📱 Phone Usage

😴 Drowsiness (Eyes Closed)

👀 Looking Away

🚨 Violation Rules
Behaviour	Threshold
Phone Usage	> 4 seconds continuous
Eyes Closed	> 3 seconds continuous
Looking Away > 5 seconds continuous
Critical Alert 2+ simultaneous violations
🧠 System Architecture
Driver App (YOLO + Rule Engine)
            ↓
      FastAPI Backend
            ↓
     Streamlit Dashboard
Communication

REST API for violation events

WebSocket broadcasting for real-time updates

📁 Project Structure
real-time-driver-behaviour-monitoring/
│
├── client/
│   └── driver.py
│
├── server/
│   └── server.py
│
├── dashboard/
│   └── dashboard.py
│
├── model/
│   └── best.pt
│
├── requirements.txt
└── README.md
⚙️ Tech Stack

Python

OpenCV

YOLO (Ultralytics)

FastAPI

WebSockets

Streamlit

Pandas

CSV Logging

🌐 API Endpoints
POST /violation

Receives violation event from driver client.

{
  "driver_id": "Driver-1",
  "type": "phone",
  "duration": 5.4,
  "status": "warning"
}
GET /drivers

Returns all current driver states.

WebSocket /ws

Broadcasts real-time driver updates to dashboard clients.

🚀 How To Run
1️⃣ Install Dependencies
pip install -r requirements.txt
2️⃣ Start Server
cd server
uvicorn server:app --reload
3️⃣ Start Dashboard
cd dashboard
streamlit run dashboard.py
4️⃣ Start Driver App
cd client
python driver.py
🔐 Demo Credentials
Driver-1 / 1234
Driver-2 / 1234
📈 Real-Time Performance

Frame-level inference

Sub-second violation detection

~1–2 second dashboard latency (poll-based)

WebSocket support for near-instant updates

This system operates as a soft real-time monitoring system.

🏆 Applications

Fleet Monitoring Systems

Commercial Vehicle Safety

Smart Transportation

AI-Based Road Safety
