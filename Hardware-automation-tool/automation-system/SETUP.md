# Hardware-Assisted Automation System - Setup Guide

## System Overview

This system captures your work PC screen via HDMI, analyzes it with OCR on your personal laptop, and automates keyboard input through a USB HID microcontroller.

### Components

- **Work PC**: Screen output via HDMI
- **HDMI Capture Card**: Connects to personal laptop (USB 3.0 recommended)
- **Personal Laptop**: Runs Python automation engine with OCR
- **Microcontroller**: Arduino Pro Micro, Raspberry Pi Pico, or Digispark
- **Work PC USB Port**: Microcontroller acts as USB keyboard

---

## Installation Steps

### 1. Python Environment Setup

#### Windows:
\`\`\`bash
# Install Python 3.9+
# Download from python.org

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install opencv-python pytesseract pillow pyserial numpy

# Install Tesseract OCR
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# During installation, note the installation path (default: C:\Program Files\Tesseract-OCR)

# Set Tesseract path in Python (add to main.py or your script):
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
\`\`\`

#### Linux:
\`\`\`bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv
sudo apt install tesseract-ocr libtesseract-dev
sudo apt install libopencv-dev python3-opencv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

pip install opencv-python pytesseract pillow pyserial numpy
\`\`\`

#### macOS:
\`\`\`bash
# Install with Homebrew
brew install python tesseract opencv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

pip install opencv-python pytesseract pillow pyserial numpy
\`\`\`

### 2. HDMI Capture Card Setup

#### Supported Capture Cards:
- Elgato HD60 S
- Magewell USB Capture
- Blackmagic Intensity Pro
- Generic USB capture cards

#### Drivers:
- Windows: Install manufacturer drivers (usually auto-detects)
- Linux: May require v4l2 drivers
- macOS: Usually plug-and-play

#### Verify Capture:
\`\`\`python
import cv2

# Test video capture
cap = cv2.VideoCapture(0)  # 0 is usually the capture card
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print("Capture card working!")
        # Save test frame
        cv2.imwrite('test_frame.jpg', frame)
    cap.release()
else:
    print("Failed to open capture card")
\`\`\`

### 3. Microcontroller Setup

#### Arduino Pro Micro:

1. Install Arduino IDE from arduino.cc
2. Install board support:
   - Tools > Board > Boards Manager
   - Search "SparkFun AVR Boards"
   - Install latest version

3. Connect Arduino Pro Micro via USB
4. Select: Tools > Board > SparkFun Pro Micro

5. Upload firmware:
   - File > Open > `firmware/arduino_pro_micro.ino`
   - Sketch > Upload

6. Find COM port:
   - Windows: Device Manager > Ports (COM#)
   - Linux: `ls /dev/ttyACM*`
   - macOS: `ls /dev/cu.usbmodem*`

#### Raspberry Pi Pico:

1. Download Arduino IDE 2.0+
2. Install RP2040 board support:
   - File > Preferences > Additional Board Managers URLs
   - Add: `https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json`
   - Tools > Board > Boards Manager > Search "Pico" > Install

3. Connect Pico while holding BOOTSEL button
4. Select: Tools > Board > Raspberry Pi Pico

5. Upload firmware (same as Arduino)

6. Find COM port: Same as Arduino Pro Micro

---

## Configuration

### config.json Structure

\`\`\`json
{
  "ocr_threshold": 0.7,
  "ocr_regions": {
    "region_name": [x1, y1, x2, y2]
  },
  "triggers": [
    {
      "name": "trigger_name",
      "keywords": ["keyword1", "keyword2"],
      "command": "TAG_NAME"
    }
  ],
  "command_mapping": {
    "TAG_NAME": ["TYPE:text", "KEY:ENTER"]
  }
}
\`\`\`

### OCR Regions

Define specific areas to scan:
- `[0, 0, 1920, 1080]` - Full 1080p screen
- `[100, 200, 500, 400]` - Specific window
- `[0, 0, 1920, 100]` - Top bar/title area

### Command Mapping

Commands sent to microcontroller:
- `TYPE:text` - Type text string
- `KEY:ENTER` - Press named key
- `COMBO:CTRL+C` - Key combination
- `DELAY:500` - Wait 500ms

### Supported Keys:
- `ENTER`, `BACKSPACE`, `DELETE`, `TAB`, `ESCAPE`
- `HOME`, `END`, `PAGE_UP`, `PAGE_DOWN`
- `UP`, `DOWN`, `LEFT`, `RIGHT`
- `SPACE`

---

## Running the System

### 1. Find your serial port:

\`\`\`bash
# Windows
mode COM1

# Linux
dmesg | grep ttyACM

# macOS
ls /dev/cu.usbmodem*
\`\`\`

### 2. Run automation:

\`\`\`bash
# Continuous mode (finds triggers, sends commands)
python main.py --config config.json --port COM3

# Test mode (uses static image)
python main.py --config config.json --port COM3 --test test_image.jpg

# Debug mode (verbose logging)
python main.py --config config.json --port COM3 --debug

# Custom interval (check every 500ms)
python main.py --config config.json --port COM3 --interval 0.5
\`\`\`

---

## Troubleshooting

### HDMI Capture Card Not Detected
\`\`\`python
import cv2
# List all available devices
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Device {i} available")
        cap.release()
\`\`\`

### Tesseract Not Found
- Windows: Set path in code: `pytesseract.pytesseract_cmd = r'C:\path\to\tesseract.exe'`
- Linux: `which tesseract` - verify installation
- macOS: `brew install tesseract`

### Serial Connection Failed
- Check USB cable
- Verify COM port: `mode COM3` (Windows) or `ls /dev/ttyACM0` (Linux)
- Check baud rate matches firmware (default 9600)
- Install CH340 drivers if needed (common for cheap microcontrollers)

### OCR Not Recognizing Text
- Adjust `ocr_threshold` in config (lower = more lenient)
- Ensure screen brightness is adequate
- Crop `ocr_regions` to focus on text areas
- Use `--debug` flag to see OCR output

### Microcontroller Not Receiving Commands
- Test with serial monitor: `pip install pyserial` then use Arduino IDE Serial Monitor
- Send test command: `TYPE:Hello\n`
- Check `--debug` output for serial errors

---

## Security Considerations

1. **USB Isolation**: Ensure microcontroller only connects to work PC
2. **Command Injection**: Sanitize trigger patterns to prevent unintended commands
3. **Screen Privacy**: HDMI capture may record sensitive data
4. **Logging**: Automation.log contains command history - protect accordingly
5. **Serial Communication**: Currently unencrypted; consider adding checksums

---

## Advanced Usage

### Custom OCR Preprocessing

Edit `ImageProcessor.preprocess()` in main.py:
\`\`\`python
def preprocess(self, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Add custom filters, thresholds, dilation, etc.
    return processed_frame
\`\`\`

### Template Matching (Alternative to OCR)

Add template matching for UI elements:
\`\`\`python
result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF)
\`\`\`

### Performance Optimization

- Reduce OCR regions to specific areas
- Increase `--interval` to 2-5 seconds
- Process lower resolution frames
- Use thread pooling for parallel processing

---

## File Structure

\`\`\`
automation-system/
├── main.py                    # Main Python automation engine
├── config.json               # Trigger and command configuration
├── automation.log            # Execution log file
├── firmware/
│   ├── arduino_pro_micro.ino # Arduino firmware
│   └── raspberry_pi_pico.ino # Pico firmware
├── test_images/
│   └── sample.jpg            # Test images for --test mode
└── SETUP.md                  # This file
\`\`\`

---

## Support

- Check `automation.log` for detailed error messages
- Use `--debug` flag for verbose output
- Verify serial connection with Arduino IDE Serial Monitor
- Test OCR independently with a static image
