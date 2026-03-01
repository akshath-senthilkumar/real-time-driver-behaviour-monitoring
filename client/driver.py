import cv2
import time
import requests
import platform
import math

if platform.system() == "Windows":
    import winsound

# ─────────────────────────────────────────────
# DEMO MODE — set True for presentation
# set False if your model works
# ─────────────────────────────────────────────
DEMO_MODE = False

CLASS_REMAP = {
    "DangerousDriving": "phone",
    "Distracted":       "looking_away",
    "Drinking":         "phone",
    "SafeDriving":      "safe",
    "SleepyDriving":    "eyes_closed",
    "Yawn":             "eyes_closed",
}

VALID_BEHAVIORS = {"phone", "eyes_closed", "looking_away"}

# ─────────────────────────────────────────────
# Credentials
# ─────────────────────────────────────────────
drivers_db = {
    "Driver-1": "1234",
    "Driver-2": "1234"
}

print("=" * 40)
print("  Driver Behaviour Monitoring System")
print("=" * 40)
username = input("Enter Driver ID: ")
password = input("Enter Password: ")

if drivers_db.get(username) != password:
    print("Invalid credentials")
    exit()

DRIVER_ID = username
print(f"\n✅ Logged in as {DRIVER_ID}")

if DEMO_MODE:
    print("")
else:
    from ultralytics import YOLO
    try:
        model = YOLO("best.pt")
        print(f"✅ Model loaded: {model.names}")
    except Exception as e:
        print(f"❌ Model load failed: {e}")
        exit()

print("Press Q to quit.\n")

# ─────────────────────────────────────────────
# Demo sequence — each state lasts 10 seconds
# Different sequence per driver for realism
# ─────────────────────────────────────────────
if DRIVER_ID == "Driver-1":
    DEMO_SEQUENCE = [
        ("SafeDriving",    10),
        ("Distracted",     12),   # triggers looking_away warning
        ("SafeDriving",     8),
        ("SleepyDriving",  10),   # triggers eyes_closed warning
        ("SafeDriving",     6),
        ("DangerousDriving",12),  # triggers phone warning
        ("SafeDriving",     8),
        ("Distracted",      8),
        ("SleepyDriving",   8),   # CRITICAL — two violations
    ]
else:
    DEMO_SEQUENCE = [
        ("SafeDriving",    8),
        ("SleepyDriving", 10),
        ("SafeDriving",    6),
        ("DangerousDriving",12),
        ("Distracted",     10),   # CRITICAL — two violations
        ("SafeDriving",    10),
        ("SleepyDriving",   8),
    ]

def get_demo_class(start_time):
    elapsed = time.time() - start_time
    total = 0
    for raw_label, duration in DEMO_SEQUENCE:
        total += duration
        if elapsed < total:
            return raw_label
    # Loop
    looped = elapsed % total
    running = 0
    for raw_label, duration in DEMO_SEQUENCE:
        running += duration
        if looped < running:
            return raw_label
    return "SafeDriving"

# ─────────────────────────────────────────────
# State
# ─────────────────────────────────────────────
timers = {"phone": None, "eyes_closed": None, "looking_away": None}
violation_start_times = {"phone": None, "eyes_closed": None, "looking_away": None}
active_violations = set()
alarm_triggered = False
last_send_time = 0
last_safe_send = 0
SEND_INTERVAL = 1.0
demo_start = time.time()


def trigger_alarm():
    if platform.system() == "Windows":
        winsound.Beep(1200, 600)
    else:
        print("\a", flush=True)


def send_to_server(v_type, duration, status):
    global last_send_time
    now = time.time()
    if now - last_send_time < SEND_INTERVAL:
        return
    last_send_time = now
    try:
        requests.post(
            "http://localhost:8000/violation",
            json={
                "driver_id": DRIVER_ID,
                "type": v_type,
                "duration": round(duration, 2),
                "status": status,
            },
            timeout=1,
        )
    except Exception:
        pass


# ─────────────────────────────────────────────
# Camera loop
# ─────────────────────────────────────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()

    # ── Get detected class ──────────────────
    if DEMO_MODE:
        raw_label = get_demo_class(demo_start)
        detected_class = CLASS_REMAP.get(raw_label, "safe")
    else:
        results = model(frame, verbose=False, conf=0.30)
        raw_label = "SafeDriving"
        detected_class = "safe"
        if results[0].boxes and len(results[0].boxes):
            boxes = results[0].boxes
            best_idx = int(boxes.conf.argmax())
            class_id = int(boxes.cls[best_idx])
            raw_label = model.names[class_id]
            detected_class = CLASS_REMAP.get(raw_label, "safe")
            box = boxes.xyxy[best_idx].cpu().numpy().astype(int)
            conf = float(boxes.conf[best_idx])
            color = (0, 0, 255) if detected_class in VALID_BEHAVIORS else (0, 200, 0)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)
            cv2.putText(frame, f"{raw_label} {conf:.2f}",
                        (box[0], box[1] - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    behavior = detected_class if detected_class in VALID_BEHAVIORS else None

    # ── Update timers ───────────────────────
    for b in timers:
        if behavior == b:
            if timers[b] is None:
                timers[b] = current_time
                violation_start_times[b] = current_time
        else:
            timers[b] = None

    active_violations.clear()
    durations = {}

    if timers["phone"] and current_time - timers["phone"] > 4:
        active_violations.add("phone")
        durations["phone"] = round(current_time - violation_start_times["phone"], 2)

    if timers["eyes_closed"] and current_time - timers["eyes_closed"] > 3:
        active_violations.add("eyes_closed")
        durations["eyes_closed"] = round(current_time - violation_start_times["eyes_closed"], 2)

    if timers["looking_away"] and current_time - timers["looking_away"] > 5:
        active_violations.add("looking_away")
        durations["looking_away"] = round(current_time - violation_start_times["looking_away"], 2)

    # ── Status ──────────────────────────────
    if len(active_violations) >= 2:
        status = "critical"
    elif len(active_violations) == 1:
        status = "warning"
    else:
        status = "safe"

    # ── Send to server ──────────────────────
    if status != "safe":
        max_dur = max(durations.values()) if durations else 0
        send_to_server(",".join(sorted(active_violations)), max_dur, status)
    else:
        if current_time - last_safe_send > 2:
            send_to_server("none", 0, "safe")
            last_safe_send = current_time

    # ── Alarm ───────────────────────────────
    if status == "critical":
        if not alarm_triggered:
            trigger_alarm()
            alarm_triggered = True
    else:
        alarm_triggered = False

    # ── HUD overlay ─────────────────────────
    status_colors = {
        "safe":     (0, 200, 0),
        "warning":  (0, 165, 255),
        "critical": (0, 0, 255),
    }
    s_color = status_colors[status]

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], 130), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    mode_tag = "[DEMO]" if DEMO_MODE else "[LIVE]"
    cv2.putText(frame, f"{mode_tag} Driver: {DRIVER_ID}",  (10, 28),  cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2)
    cv2.putText(frame, f"Detected: {raw_label}",           (10, 58),  cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200,200,200), 2)
    cv2.putText(frame, f"Mapped:   {detected_class}",      (10, 88),  cv2.FONT_HERSHEY_SIMPLEX, 0.70, (180,180,180), 2)
    cv2.putText(frame, f"Status:   {status.upper()}",      (10, 118), cv2.FONT_HERSHEY_SIMPLEX, 0.75, s_color, 2)

    if active_violations:
        txt = "Violations: " + ", ".join(sorted(active_violations))
        cv2.putText(frame, txt, (10, 148), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 2)

    # Red border flash on critical
    if status == "critical":
        cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), (0, 0, 255), 6)

    cv2.imshow(f"Driver Monitor — {DRIVER_ID}", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("Session ended.")
