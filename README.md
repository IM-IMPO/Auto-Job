# Auto-Job
If this plan works, I don't have to work anymore.


# Autonomous USB Keyboard Automation System

(Screen Recognition + Hardware HID Keystroke Execution)

## Overview

This project enables you to automate repetitive keyboard workflows on a
work PC that does not allow software installation, using:

-   Your personal laptop for screen analysis (AI / OCR / detection)
-   A USB device that acts like a keyboard (HID)
-   A hardware-based screen capture method (no software on work PC)

This system types automatically based on what it sees on the work PC
monitor.

## Features

-   No software installation on work PC
-   USB device acts as a real keyboard
-   AI analysis done entirely on your personal laptop
-   Works with OCR, image recognition, and logic automation
-   Fully offline option available

## System Architecture

     Work PC (no installs)
          │
       HDMI OUT
          │
    ┌──────────────┐
    │ HDMI Capture │
    └──────────────┘
          │ USB
          ▼
     Personal Laptop (AI processing)
          │ Serial/WiFi
          ▼
    Microcontroller USB HID (Keyboard)
          │ USB
          ▼
    Work PC receives keystrokes

## Required Hardware

### 1. USB HID Microcontroller (choose one)

  Device                 Price   Notes
  ---------------------- ------- --------------------------------
  Raspberry Pi Pico      ₱250    Easiest and stable HID
  Arduino Pro Micro      ₱350    Simple HID
  Digispark ATTiny85     ₱120    Very small but can be unstable
  Raspberry Pi Zero 2W   ₱900    Best if WiFi control is needed

### 2. HDMI Capture Method

#### A. HDMI Capture Card (recommended)

-   Price: ₱400--₱700\
-   Plug-and-play\
-   Laptop sees the work PC screen as a webcam

#### B. Webcam pointed at monitor

-   Works, but glare may reduce OCR accuracy

### 3. Additional Requirements

-   HDMI cable
-   USB cable for microcontroller
-   USB capture card
-   Personal laptop with Python installed

## Required Software (on your personal laptop only)

Install dependencies:

    pip install opencv-python pytesseract pyserial pillow

Install Tesseract OCR for Windows:\
https://github.com/UB-Mannheim/tesseract/wiki

## Logic Flow

1.  Capture the screen using HDMI capture card\
2.  Laptop analyzes the frame with AI/OCR\
3.  If trigger text is detected (example: "Service Offering")\
4.  Laptop sends a command to a microcontroller\
5.  Microcontroller types predefined keystrokes

## Python Script: Screen Recognition

``` python
# screen_processor.py
import cv2
import pytesseract
import serial
import time

ser = serial.Serial('COM5', 9600)  # Arduino/Pico COM port

cap = cv2.VideoCapture(0)  # HDMI capture card input

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    text = pytesseract.image_to_string(frame).lower()

    if "service offering" in text:
        print("Detected: SERVICE OFFERING")
        ser.write(b"TAG1\n")

    cv2.imshow("Feed", frame)
    if cv2.waitKey(1) == ord('q'):
        break
```

## Arduino / Pico HID Code

### Example (Arduino Pro Micro)

``` cpp
#include <Keyboard.h>

void setup() {
  Keyboard.begin();
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');

    if (cmd == "TAG1") {
      Keyboard.print("112567");
      Keyboard.write(KEY_RETURN);
    }
  }
}
```

## Testing Procedure

1.  Connect HDMI from work PC → capture card → personal laptop\
2.  Connect microcontroller to work PC via USB\
3.  Run the Python detection script on your laptop\
4.  Display the trigger text on your work PC screen\
5.  The USB HID device will type automatically

## Security Notes

-   Does not install software on work PC\
-   Only acts as a keyboard\
-   Ensure this automation complies with your workplace policies

## Folder Structure

    /
    ├── README.md
    ├── screen_processor.py
    ├── arduino_hid.ino
    └── images/

## Troubleshooting

### OCR not detecting?

-   Improve lighting
-   Adjust camera angle
-   Crop specific screen regions

### HID not typing?

-   Confirm COM port
-   Try different USB cable
-   Test with a simple print command

## End

This document provides everything needed to create a hardware-based AI
automation device that types automatically based on what it sees on the
screen.
