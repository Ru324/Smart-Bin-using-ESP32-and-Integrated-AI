"""
SmartBin — AI Inference Pipeline
Host-side Python script for waste classification + ESP32 serial control

Course: Microprocessor and Microcontroller (MPMC)
VIT Vellore | Prof. Veerapu Goutham | C1 + TC1

Team:
    Prasannajeet Mangaraj  - 24BEC0509
    Ruturaj Inamdar        - 24BEC0354
    Pranav Sardhara        - 24BEC0225
    Apoorva R              - 24BEC0307

Description:
    Captures webcam frames via OpenCV, runs waste classification
    using a Roboflow-hosted model, and sends UART commands to ESP32
    when a high-confidence prediction is stable for 3 seconds.

Requirements:
    pip install inference opencv-python pyserial

Usage:
    1. Update API_KEY and ESP32_PORT below
    2. Run: python inference_pipeline.py
    3. Hold object in front of webcam — bin flap opens automatically
    4. Press 'q' to quit
"""

import cv2
import time
import serial
from inference import get_model

# ─────────────────────────────────────────────
#  CONFIGURATION — Edit these before running
# ─────────────────────────────────────────────
MODEL_ID       = "waste-classifier-3himj/2"
API_KEY        = "YOUR_ROBOFLOW_API_KEY"     # Replace with your key
ESP32_PORT     = "COM6"                       # Windows: COMx | Linux/Mac: /dev/ttyUSB0
BAUD_RATE      = 115200

# Classification thresholds
CONF_THRESHOLD = 0.95   # 95% confidence minimum to consider a detection
STABLE_TIME    = 3      # Seconds the same label must persist before triggering
FLAP_WAIT_TIME = 5      # Seconds to wait after a flap is opened (3s open + cooldown)

# ─────────────────────────────────────────────
#  Label → ESP32 Command Mapping
# ─────────────────────────────────────────────
LABEL_TO_COMMAND = {
    "paper":                  "R",
    "recyclable plastic":     "R",
    "metal":                  "R",
    "cardboard":              "R",
    "non-recyclable plastic": "N",
    "stationary":             "N",
    "e-waste":                "E",
    "nothing":                None,   # No flap — sends 'X'
}

COMMAND_TO_FLAP_NAME = {
    "R": "RECYCLABLE",
    "N": "NON-RECYCLABLE",
    "E": "E-WASTE",
}

# ─────────────────────────────────────────────
#  Overlay colour constants (BGR)
# ─────────────────────────────────────────────
GREEN  = (0, 255, 0)
RED    = (0, 0, 255)
YELLOW = (0, 255, 255)
WHITE  = (255, 255, 255)
CYAN   = (255, 255, 0)

# ─────────────────────────────────────────────
#  Initialise model and serial
# ─────────────────────────────────────────────
print("Loading Roboflow model...")
model = get_model(model_id=MODEL_ID, api_key=API_KEY)
print("Model loaded successfully.")

print(f"Connecting to ESP32 on {ESP32_PORT} @ {BAUD_RATE} baud...")
ser = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=1)
time.sleep(2)   # Allow ESP32 boot time
print("ESP32 connected.")

# ─────────────────────────────────────────────
#  Initialise webcam
# ─────────────────────────────────────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Cannot open camera. Check connection.")
    ser.close()
    exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print("Camera streaming started. Press 'q' to quit.")

# ─────────────────────────────────────────────
#  State variables
# ─────────────────────────────────────────────
prev_time        = 0
stable_label     = None
stable_start     = None
busy             = False     # True while a flap is open / cooling down

# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────
while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame grab failed — retrying...")
        continue

    detected_label = None
    detected_conf  = 0.0

    # Run inference
    try:
        results = model.infer(frame)[0]
        if results.predictions:
            top             = results.predictions[0]
            detected_label  = top.class_name.lower().strip()
            detected_conf   = top.confidence
            label_text      = f"{top.class_name} ({detected_conf * 100:.1f}%)"
            cv2.putText(frame, label_text, (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN, 2)
        else:
            cv2.putText(frame, "No object detected", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)

    except Exception as e:
        cv2.putText(frame, "Inference Error", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)
        print(f"Inference error: {e}")

    # Stability check + flap actuation
    if detected_label and detected_conf >= CONF_THRESHOLD and not busy:
        if stable_label == detected_label:
            elapsed = time.time() - stable_start
            cv2.putText(frame, f"Stable: {elapsed:.1f}/{STABLE_TIME}s",
                        (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, YELLOW, 2)

            if elapsed >= STABLE_TIME:
                cmd = LABEL_TO_COMMAND.get(detected_label, None)

                if cmd is None:
                    # Mapped to "nothing" — send X, no flap
                    print(f"Detected: {detected_label} → No flap (sending X)")
                    ser.write(b'X')
                    stable_label = None
                    stable_start = None
                else:
                    flap_name = COMMAND_TO_FLAP_NAME.get(cmd, "UNKNOWN")
                    print(f"Detected: {detected_label} → Sending '{cmd}' → {flap_name} flap")
                    ser.write(cmd.encode())

                    cv2.putText(frame, f"OPENING {flap_name} FLAP",
                                (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, CYAN, 2)
                    cv2.imshow("SmartBin — Waste Classifier", frame)
                    cv2.waitKey(1)

                    busy         = True
                    time.sleep(FLAP_WAIT_TIME)  # Block while flap operates

                    # Reset state after flap cycle
                    stable_label = None
                    stable_start = None
                    busy         = False
        else:
            # New label — reset stability timer
            stable_label = detected_label
            stable_start = time.time()
    else:
        stable_label = None
        stable_start = None

    # FPS counter
    curr_time = time.time()
    fps       = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time

    cv2.putText(frame, f"FPS: {int(fps)}", (20, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)
    cv2.putText(frame, "Press 'q' to quit", (400, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)

    cv2.imshow("SmartBin — Waste Classifier", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ─────────────────────────────────────────────
#  Cleanup
# ─────────────────────────────────────────────
print("Shutting down...")
try:
    ser.write(b'C')   # Force close all flaps on exit
except Exception:
    pass

ser.close()
cap.release()
cv2.destroyAllWindows()
print("System stopped.")
