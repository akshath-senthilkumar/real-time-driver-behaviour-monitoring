🚗 Real-Time Driver Behaviour Monitoring System
📌 Overview

A real-time multi-driver behaviour monitoring platform that detects unsafe driving behaviours using computer vision and displays live violation alerts on a centralized dashboard.

This system supports multiple drivers simultaneously and updates their status dynamically with rule-based violation detection.

🎯 Problem Statement

Monitor driver behaviour in real time and detect:

📱 Phone usage

😴 Drowsiness (eyes closed)

👀 Looking away from road

Trigger alerts when violations exceed time thresholds and display them live on a central dashboard.

🧠 System Architecture
Driver App (YOLO + Rule Engine)
            ↓
      FastAPI Server
            ↓
  Streamlit Dashboard (Live Updates)

Communication:

REST API for violation events

WebSocket broadcasting for real-time dashboard updates

⚙️ Tech Stack

Python

OpenCV

YOLO (Ultralytics)

FastAPI

WebSockets

Streamlit

Pandas

CSV Logging

🚨 Violation Rules
Behaviour	Trigger Condition
Phone Usage	> 4 seconds continuous
Eyes Closed	> 3 seconds continuous
Looking Away	> 5 seconds continuous
Critical Alert	2+ simultaneous violations
👥 Multi-Driver Support

Driver login authentication

Independent violation tracking per driver

Active / Inactive detection (based on heartbeat)

Centralized dashboard monitoring

🖥 Driver App Features

Webcam real-time inference

YOLO object detection

Rule-based time tracking

Audio alert on critical violation

HUD overlay with status

Sends structured JSON events to server

📊 Dashboard Features

Live auto-updating interface

Driver status cards

Active driver detection

Critical alert blinking highlight

Violation duration tracking

CSV violation history download

Bar chart analytics

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

Returns current driver states.

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
python driver_app.py
🔐 Demo Credentials
Driver-1 / 1234
Driver-2 / 1234
📷 Screenshots

(Add images here)

screenshots/dashboard.png
screenshots/driver_app.png
📈 Real-Time Performance

Frame-level inference (continuous)

Sub-second violation detection

~1–2 second dashboard latency (poll-based)

Supports WebSocket real-time broadcasting

This system operates as a soft real-time monitoring system.

🏗 Future Improvements

Database integration (PostgreSQL / MongoDB)

JWT Authentication

Dockerization

Cloud deployment (Render / AWS)

SMS / Email alert integration

Edge deployment (Raspberry Pi)

🏆 Applications

Fleet management systems

Smart transportation

Commercial vehicle monitoring

AI-based road safety systems

📜 License

MIT License

🔥 Add This At Top (Very Important)

Add badges:

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![YOLO](https://img.shields.io/badge/YOLO-ObjectDetection-red)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-orange)

Recruiters love badges.
