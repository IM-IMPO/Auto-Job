# Hardware Wiring Guide

## HDMI Capture Card Connection

\`\`\`
Work PC HDMI OUT → HDMI Capture Card USB → Personal Laptop USB Port
\`\`\`

No drivers needed on work PC - it's completely unaware of the capture.

---

## Microcontroller to Work PC

### Option 1: USB Direct (Recommended)

\`\`\`
Microcontroller USB → Work PC USB Port
\`\`\`

The microcontroller presents itself as a standard HID keyboard - no driver installation needed.

### Option 2: Serial Over USB to Network Adapter (Advanced)

For remote setups, use USB-to-WiFi adapter on microcontroller for wireless command delivery.

---

## Physical Setup Diagram

\`\`\`
WORK PC                      PERSONAL LAPTOP
┌─────────────────┐          ┌──────────────────┐
│                 │          │                  │
│ ┌─────────────┐ │          │ ┌──────────────┐ │
│ │ HDMI OUTPUT │─────────────→│ HDMI Capture │ │
│ └─────────────┘ │          │ └──────────────┘ │
│                 │          │                  │
│ ┌─────────────┐ │          │ Python Engine    │
│ │ USB (HID)   │←────────────── Serial Port     │
│ └─────────────┘ │   (Keyboard Commands)       │
└─────────────────┘          └──────────────────┘
    MICROCONTROLLER
    ┌──────────┐
    │ Arduino  │
    │ Pro Micro│
    └──────────┘
    (appears as
     USB keyboard
     to Work PC)
\`\`\`

---

## Arduino Pro Micro Pinout

\`\`\`
        USB
    ┌─────────┐
GND─┤1       12├─ D12/MISO
TX1─┤2       11├─ D11/MOSI
RX0─┤3       10├─ D10/SS
    │4        9├─ D9/A9
RST─┤5        8├─ D8/A8
    │6        7├─ D7/A7
    └─────────┘
5V connected to USB power
GND for ground reference
\`\`\`

All serial communication happens over USB - no separate UART needed.

---

## Raspberry Pi Pico Pinout (Relevant Pins)

\`\`\`
        USB
    ┌─────────┐
1  │GP0      40│ VBUS
2  │GP1      39│ VSYS
3  │GND      38│ GND
...
20 │GND      21│ GP16
    └─────────┘
\`\`\`

Uses USB CDC (serial over USB) - works the same as Arduino for our purposes.

---

## Power Considerations

- **Arduino Pro Micro**: 5V from USB
- **Pico**: 5V from USB (5V tolerant)
- **Capture Card**: 5V USB 3.0 recommended (high bandwidth)
- **Microcontroller Power**: Shared with keyboard input

No external power supplies needed for this setup.

---

## Troubleshooting Connections

1. **HDMI Not Detected**: Check HDMI cable both ends, try different port
2. **Capture Card Not Recognized**: Try different USB port (USB 3.0 if available)
3. **Microcontroller Not Recognized**: Install USB drivers if needed
4. **Serial Communication Fails**: Check USB cable quality, try different port
