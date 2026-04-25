/*
 * SmartBin — Automated AI Waste Classifier
 * ESP32 Firmware
 *
 * Course: Microprocessor and Microcontroller (MPMC)
 * VIT Vellore | Prof. Veerapu Goutham | C1 + TC1
 *
 * Team:
 *   Prasannajeet Mangaraj  - 24BEC0509
 *   Ruturaj Inamdar        - 24BEC0354
 *   Pranav Sardhara        - 24BEC0225
 *   Apoorva R              - 24BEC0307
 *
 * Description:
 *   Receives single-character UART commands from host Python script
 *   and actuates one of three SG90 servo motors to open the
 *   corresponding bin flap for 3 seconds, then closes it.
 *
 * Command Protocol:
 *   'R' → Open Recyclable flap (GPIO 4)
 *   'N' → Open Non-Recyclable flap (GPIO 5)
 *   'E' → Open E-Waste flap (GPIO 18)
 *   'C' → Force close all flaps
 *   'X' → Nothing detected, no action
 *
 * Hardware:
 *   ESP32 Dev Board (240 MHz dual-core)
 *   3x SG90 Servo Motors (50 Hz, 500–2400 µs pulse width)
 *   USB (Type-A to Micro-B) for power + UART bridge
 *
 * Library Required: ESP32Servo
 *   Install via Arduino Library Manager
 */

#include <ESP32Servo.h>

// ----- Servo Objects -----
Servo recyclableServo;
Servo nonRecyclableServo;
Servo ewasteServo;

// ----- Pin Assignments -----
const int recyclablePin    = 4;
const int nonRecyclablePin = 5;
const int ewastePin        = 18;

// ----- Servo Angle Config -----
const int CLOSE_ANGLE = 0;
const int OPEN_ANGLE  = 90;

// ----- Timing -----
const int FLAP_OPEN_MS = 3000;  // Flap stays open for 3 seconds
const int INIT_DELAY_MS = 1000; // Startup stabilization delay

// ----- Helper: Close all flaps -----
void closeAllFlaps() {
  recyclableServo.write(CLOSE_ANGLE);
  nonRecyclableServo.write(CLOSE_ANGLE);
  ewasteServo.write(CLOSE_ANGLE);
}

// ----- Setup -----
void setup() {
  Serial.begin(115200);

  // Set PWM frequency for all servos (standard 50 Hz)
  recyclableServo.setPeriodHertz(50);
  nonRecyclableServo.setPeriodHertz(50);
  ewasteServo.setPeriodHertz(50);

  // Attach servos with min/max pulse widths in microseconds
  recyclableServo.attach(recyclablePin, 500, 2400);
  nonRecyclableServo.attach(nonRecyclablePin, 500, 2400);
  ewasteServo.attach(ewastePin, 500, 2400);

  // Initialize all flaps to closed position
  closeAllFlaps();
  delay(INIT_DELAY_MS);

  Serial.println("ESP32 Ready — SmartBin 3-Servo System");
  Serial.println("Awaiting commands: R / N / E / C / X");
}

// ----- Main Loop -----
void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    // Always close all flaps before any action
    closeAllFlaps();

    if (cmd == 'R') {
      Serial.println("[ACTION] Opening Recyclable Flap");
      recyclableServo.write(OPEN_ANGLE);
      delay(FLAP_OPEN_MS);
      closeAllFlaps();
      Serial.println("[STATUS] Recyclable Flap Closed");
    }
    else if (cmd == 'N') {
      Serial.println("[ACTION] Opening Non-Recyclable Flap");
      nonRecyclableServo.write(OPEN_ANGLE);
      delay(FLAP_OPEN_MS);
      closeAllFlaps();
      Serial.println("[STATUS] Non-Recyclable Flap Closed");
    }
    else if (cmd == 'E') {
      Serial.println("[ACTION] Opening E-Waste Flap");
      ewasteServo.write(OPEN_ANGLE);
      delay(FLAP_OPEN_MS);
      closeAllFlaps();
      Serial.println("[STATUS] E-Waste Flap Closed");
    }
    else if (cmd == 'C') {
      closeAllFlaps();
      Serial.println("[STATUS] Force Closed — All Flaps");
    }
    else if (cmd == 'X') {
      Serial.println("[INFO] Nothing detected — No flap opened");
    }
    else {
      Serial.print("[WARN] Unknown command received: ");
      Serial.println(cmd);
    }
  }
}
