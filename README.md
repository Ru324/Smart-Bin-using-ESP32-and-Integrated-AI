#  SmartBin — Automated AI Waste Classifier using ESP32

<p align="center">
  <img src="https://img.shields.io/badge/Platform-ESP32-blue?style=for-the-badge&logo=espressif" />
  <img src="https://img.shields.io/badge/AI-Roboflow-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Language-C%2B%2B%20%7C%20Python-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Framework-Arduino-teal?style=for-the-badge&logo=arduino" />
  <img src="https://img.shields.io/badge/Status-Working%20Prototype-brightgreen?style=for-the-badge" />
</p>

> **Course Project — Microprocessor and Microcontroller (MPMC)**  
> Vellore Institute of Technology, Vellore | Prof. Veerapu Goutham | Slot: C1 + TC1

---

##  Team Members

| Name | Registration No. |
|------|-----------------|
| Prasannajeet Mangaraj | 24BEC0509 |
| Ruturaj Inamdar | 24BEC0354 |
| Pranav Sardhara | 24BEC0225 |
| Apoorva R | 24BEC0307 |

---

##  Project Overview

**SmartBin** is an IoT-enabled, AI-powered waste management system built around the **ESP32 microcontroller**. It eliminates passive waste disposal by automatically classifying waste into three categories — **Recyclable**, **Non-Recyclable**, and **E-Waste** — and physically directing it to the correct bin compartment via servo-actuated flaps.

A **Roboflow-hosted object detection model** runs inference on a live webcam feed via Python, sends single-character UART commands to the ESP32, and the ESP32 actuates the correct SG90 servo motor to open the corresponding flap.

### The Problem it Solves

Traditional bins are completely passive — they have no way of knowing what goes into them or how full they are. SmartBin addresses both by embedding:
- **Automation** → touchless lid operation
- **AI inference** → waste-type classification at the point of disposal

---

##  System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   HOST PC (Python)                      │
│                                                         │
│  ┌──────────────┐    ┌──────────────────────────────┐  │
│  │  Webcam Feed │───▶│  OpenCV Frame Capture        │  │
│  │  640×480     │    │  + Roboflow Inference SDK    │  │
│  └──────────────┘    │  + 95% Confidence Filter     │  │
│                      │  + 3s Stability Window       │  │
│                      └──────────────┬───────────────┘  │
└─────────────────────────────────────┼───────────────────┘
                                      │ UART 115200 baud
                                      │ Single char (R/N/E/C/X)
                                      ▼
┌─────────────────────────────────────────────────────────┐
│                   ESP32 Dev Board                       │
│                                                         │
│   Serial.read()  ──▶  Command Parser                   │
│                            │                           │
│              ┌─────────────┼─────────────┐             │
│              ▼             ▼             ▼             │
│         GPIO 4         GPIO 5        GPIO 18           │
│       Recyclable    Non-Recyclable   E-Waste           │
│       SG90 Servo     SG90 Servo     SG90 Servo         │
│       (0°→90°)       (0°→90°)       (0°→90°)          │
└─────────────────────────────────────────────────────────┘
```

### Three-Layer Architecture

| Layer | Components |
|-------|-----------|
| **Sensor / Actuator** | 3× SG90 servos, laptop webcam (640×480 @ 30fps) |
| **Processing** | ESP32 (PWM + UART logic), Python inference pipeline |
| **Output / Communication** | OpenCV overlay (label, confidence, FPS), Serial echo logs |

---

##  Hardware Components

| Component | Spec | Role |
|-----------|------|------|
| ESP32 Dev Board | Dual-core 240 MHz, 34 GPIO | Main controller |
| SG90 Servo Motors × 3 | 180°, 5V, ~1.8 kg·cm | Actuate bin flaps |
| Laptop Webcam | 640×480 @ 30 fps | Live image capture |
| USB Cable (Type-A to Micro-B) | — | Power + UART bridge |
| Jumper Wires | Male-to-male, 20 cm | Internal wiring |
| Cardboard Enclosure | Black chart paper finish | Bin body / prototype |
| 5V Power Supply | Via laptop USB | ESP32 + 3 servos |

### Wiring

```
ESP32 Pin 4   ──────── SG90 Signal (Recyclable)
ESP32 Pin 5   ──────── SG90 Signal (Non-Recyclable)
ESP32 Pin 18  ──────── SG90 Signal (E-Waste)
ESP32 GND     ──────── All Servo GNDs
5V (USB)      ──────── All Servo VCC
```

---

##  AI Model

- **Platform:** Roboflow Hosted Inference
- **Model ID:** `waste-classifier-3himj/2`
- **Categories:** Recyclable, Non-Recyclable, E-Waste
- **Confidence Threshold:** 0.95 (95%) — prevents false triggers
- **Stability Window:** 3 seconds — prediction must hold before actuation

### Label → Command Mapping

| Detected Label | UART Command | Flap |
|---------------|-------------|------|
| paper, recyclable plastic, metal, cardboard | `R` | Recyclable |
| non-recyclable plastic, stationary | `N` | Non-Recyclable |
| e-waste | `E` | E-Waste |
| nothing | `X` | No action |
| Force close | `C` | All flaps closed |

### Dataset

> Labelled images across all three categories, captured under varied lighting conditions to improve model generalization.

 [Download Dataset from Google Drive](https://drive.google.com/file/d/1H8TTzF6n1n7X2CH8LvX7BQnGIqn2uip/view?usp=sharing)

---

##  Repository Structure

```
smartbin-esp32/
├── firmware/
│   └── smartbin_esp32.ino       # ESP32 Arduino firmware
├── python/
│   └── inference_pipeline.py    # Python AI inference + serial control
├── docs/
│   └── system_architecture.png  # Architecture diagram (optional)
├── requirements.txt             # Python dependencies
├── .gitignore
└── README.md
```

---

##  Getting Started

### Prerequisites

- Arduino IDE with ESP32 board support installed
- Python 3.8+
- Roboflow account + API key
- `inference` SDK, `opencv-python`, `pyserial`

### 1. Flash ESP32 Firmware

1. Open `firmware/smartbin_esp32.ino` in Arduino IDE
2. Install the **ESP32Servo** library via Library Manager
3. Select board: **ESP32 Dev Module**
4. Connect ESP32 via USB, select the correct COM port
5. Upload the sketch

### 2. Set Up Python Environment

```bash
git clone https://github.com/YOUR_USERNAME/smartbin-esp32.git
cd smartbin-esp32

pip install -r requirements.txt
```

### 3. Configure and Run

Open `python/inference_pipeline.py` and update:

```python
API_KEY   = "YOUR_ROBOFLOW_API_KEY"
ESP32_PORT = "COM6"      # Windows: COMx | Linux/Mac: /dev/ttyUSB0
```

Then run:

```bash
python python/inference_pipeline.py
```

The live webcam window opens. Hold an object in front of the camera — the system will classify, confirm over 3 seconds, and open the correct flap automatically. Press `q` to quit.

---

##  Performance Observations

| Test Object | Classification | Result |
|-------------|---------------|--------|
| Paper sheet | Recyclable |  Correct |
| Cardboard | Recyclable |  Correct |
| Plastic bottle | Recyclable |  Correct |
| Mobile phone | E-Waste |  Correct |
| Non-recyclable wrapper | Non-Recyclable |  Correct |

The **3-second stability window** was the single most impactful design decision — it eliminated false triggers that occurred in early testing when the model flickered between labels on edge-case objects.

---

##  Known Limitations

| Limitation | Description |
|-----------|-------------|
| **Lighting sensitivity** | Classification accuracy degrades in very low ambient light |
| **Servo drift** | Minor positional drift observed after ~50 consecutive operations due to cardboard lid weight |
| **API dependency** | Roboflow inference requires an active internet connection — offline use needs TFLite migration |
| **Single-object constraint** | Only the top-confidence prediction triggers a flap; simultaneous multi-object input is not handled |
| **Serial buffer overflow** | In high-frequency testing, occasional missed commands — a handshake/ACK protocol would fix this |
| **Enclosure fragility** | Cardboard build requires periodic re-taping; a 3D-printed or acrylic enclosure is needed for production |

---

##  Future Enhancements

- [ ] Replace Roboflow API with **TFLite model on ESP32-CAM** for fully offline operation
- [ ] Add **HC-SR04 ultrasonic sensors** per compartment for fill-level monitoring
- [ ] Integrate **Wi-Fi MQTT** to push logs to ThingSpeak or Node-RED cloud dashboard
- [ ] Add **buzzer / LED** feedback after classification
- [ ] Expand dataset to include glass, organic, and hazardous waste categories
- [ ] Add **LCD / OLED display** for subcategory display and fill-level readout
- [ ] Implement **ACK handshake protocol** over UART to prevent missed commands

---

##  MPMC Concepts Demonstrated

This project is a practical demonstration of core MPMC concepts:

| Concept | Application |
|---------|------------|
| **GPIO** | Servo signal pins (4, 5, 18) |
| **PWM** | SG90 servo control (50 Hz, 500–2400 µs pulse width) |
| **UART** | 115200 baud serial between ESP32 and host PC |
| **Interrupt-driven programming** | `Serial.available()` polling in loop |
| **Timer/Delay** | 3-second flap open window, 1s init delay |

---

This project is submitted as an academic course project at VIT Vellore. Code is open for educational reference.

---

<p align="center">Made with electronic components and cardboard at VIT Vellore</p>
