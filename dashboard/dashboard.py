import streamlit as st
import asyncio
import websockets
import json
import pandas as pd
import os
import time
import threading
import requests

st.set_page_config(
    page_title="Driver Monitor Dashboard",
    page_icon="🚗",
    layout="wide"
)

# ─────────────────────────────────────────────
# Custom CSS for visual polish
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .critical-box {
        background: #ff000022;
        border: 2px solid #ff0000;
        border-radius: 10px;
        padding: 10px;
        animation: blink 1s infinite;
    }
    .warning-box {
        background: #ffa50022;
        border: 2px solid #ffa500;
        border-radius: 10px;
        padding: 10px;
    }
    .safe-box {
        background: #00800022;
        border: 2px solid #00aa00;
        border-radius: 10px;
        padding: 10px;
    }
    .inactive-box {
        background: #88888822;
        border: 2px solid #888888;
        border-radius: 10px;
        padding: 10px;
        opacity: 0.7;
    }
    @keyframes blink {
        0%   { border-color: #ff0000; }
        50%  { border-color: #ff000055; }
        100% { border-color: #ff0000; }
    }
    .driver-name { font-size: 22px; font-weight: bold; margin-bottom: 5px; }
    .metric-label { color: #aaaaaa; font-size: 13px; }
    .metric-value { font-size: 16px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🚗 Driver Behaviour Monitoring Dashboard")
st.markdown("---")

# ─────────────────────────────────────────────
# CSV Download
# ─────────────────────────────────────────────
col_dl1, col_dl2 = st.columns([1, 3])
with col_dl1:
    if os.path.exists("violations_log.csv"):
        with open("violations_log.csv", "rb") as f:
            st.download_button(
                label="📥 Download Violation Log",
                data=f,
                file_name="violations_log.csv",
                mime="text/csv"
            )
    else:
        st.info("No violations logged yet.")

# ─────────────────────────────────────────────
# Shared state (thread-safe via session state)
# ─────────────────────────────────────────────
if "drivers_data" not in st.session_state:
    st.session_state.drivers_data = {}

if "last_update" not in st.session_state:
    st.session_state.last_update = 0

# ─────────────────────────────────────────────
# Fetch data from server (REST fallback)
# ─────────────────────────────────────────────
def fetch_drivers():
    try:
        r = requests.get("http://localhost:8000/drivers", timeout=2)
        return r.json()
    except Exception:
        return {}


def render_driver_card(driver_id, info, col):
    with col:
        now = time.time()
        is_active = now - info.get("last_seen", 0) < 10
        status = info.get("status", "safe")

        if not is_active:
            box_class = "inactive-box"
            status_display = "⚫ INACTIVE"
            status_color = "#888888"
        elif status == "critical":
            box_class = "critical-box"
            status_display = "🚨 CRITICAL"
            status_color = "#ff4444"
        elif status == "warning":
            box_class = "warning-box"
            status_display = "⚠️ WARNING"
            status_color = "#ffa500"
        else:
            box_class = "safe-box"
            status_display = "✅ SAFE"
            status_color = "#00cc00"

        violation = info.get("violation", "none")
        duration = info.get("duration", 0)
        last_time = info.get("time", "—")

        # Active badge
        active_badge = "🟢 ACTIVE" if is_active else "🔴 INACTIVE"

        st.markdown(f"""
        <div class="{box_class}">
            <div class="driver-name">🧑‍💼 {driver_id}</div>
            <div style="margin-bottom:8px;">{active_badge}</div>
            <div style="color:{status_color}; font-size:20px; font-weight:bold; margin-bottom:8px;">
                {status_display}
            </div>
            <div class="metric-label">Violation</div>
            <div class="metric-value" style="color:#ff6666;">{violation if violation != 'none' else '—'}</div>
            <br>
            <div class="metric-label">Duration</div>
            <div class="metric-value">{duration} sec</div>
            <br>
            <div class="metric-label">Last Update</div>
            <div class="metric-value">{last_time}</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Main display loop (auto-refresh via st.rerun)
# ─────────────────────────────────────────────
status_bar = st.empty()
drivers_placeholder = st.empty()
chart_placeholder = st.empty()

REFRESH_INTERVAL = 1.5  # seconds

while True:
    drivers_data = fetch_drivers()

    if drivers_data:
        st.session_state.drivers_data = drivers_data

    data = st.session_state.drivers_data

    with drivers_placeholder.container():
        if not data:
            st.info("⏳ Waiting for drivers to connect... Make sure server.py is running.")
        else:
            # Summary bar
            now = time.time()
            active_count = sum(1 for d in data.values() if now - d.get("last_seen", 0) < 10)
            critical_count = sum(1 for d in data.values()
                                  if d.get("status") == "critical" and now - d.get("last_seen", 0) < 10)
            warning_count = sum(1 for d in data.values()
                                 if d.get("status") == "warning" and now - d.get("last_seen", 0) < 10)

            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Total Drivers", len(data))
            s2.metric("🟢 Active", active_count)
            s3.metric("⚠️ Warnings", warning_count)
            s4.metric("🚨 Critical", critical_count)

            st.markdown("---")

            # Driver cards
            num_drivers = len(data)
            cols = st.columns(max(num_drivers, 1))

            for i, (driver_id, info) in enumerate(data.items()):
                render_driver_card(driver_id, info, cols[i % len(cols)])

    # Violation chart
    with chart_placeholder.container():
        if os.path.exists("violations_log.csv"):
            try:
                df = pd.read_csv("violations_log.csv")
                if not df.empty:
                    st.markdown("---")
                    st.subheader("📊 Violation History")

                    c1, c2 = st.columns(2)

                    with c1:
                        v_counts = df["Violation"].value_counts().reset_index()
                        v_counts.columns = ["Violation", "Count"]
                        st.bar_chart(v_counts.set_index("Violation"))

                    with c2:
                        recent = df.tail(20)[["Driver", "Violation", "Status", "Time"]]
                        st.dataframe(recent, use_container_width=True)
            except Exception:
                pass

    time.sleep(REFRESH_INTERVAL)
    st.rerun()
