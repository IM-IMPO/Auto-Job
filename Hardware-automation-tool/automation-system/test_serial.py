#!/usr/bin/env python3
"""
Serial Communication Test Utility
Tests connection to microcontroller and basic command execution.
"""

import serial
import time
import sys
from pathlib import Path


def test_serial_connection(port: str, baudrate: int = 9600) -> bool:
    """Test basic serial connection."""
    try:
        ser = serial.Serial(port, baudrate, timeout=2)
        time.sleep(2)  # Wait for microcontroller
        
        print(f"[OK] Connected to {port} at {baudrate} baud")
        
        # Send ping
        ser.write(b"PING\n")
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response == "PONG":
                print(f"[OK] Received PONG - Microcontroller responsive")
                ser.close()
                return True
        
        ser.close()
        return False
    
    except serial.SerialException as e:
        print(f"[ERROR] Serial connection failed: {e}")
        return False


def test_keyboard_commands(port: str, baudrate: int = 9600):
    """Test basic keyboard commands."""
    try:
        ser = serial.Serial(port, baudrate, timeout=2)
        time.sleep(2)
        
        commands = [
            ("TYPE:Hello", "Type 'Hello'"),
            ("KEY:ENTER", "Press Enter"),
            ("TYPE:World", "Type 'World'"),
            ("DELAY:500", "Wait 500ms"),
            ("KEY:BACKSPACE", "Press Backspace"),
        ]
        
        for cmd, description in commands:
            print(f"Sending: {description} ({cmd})")
            ser.write(f"{cmd}\n".encode('utf-8'))
            time.sleep(1)
        
        ser.close()
        print("[OK] All commands executed")
    
    except Exception as e:
        print(f"[ERROR] Command test failed: {e}")


def list_serial_ports():
    """List available serial ports."""
    import platform
    
    if platform.system() == "Windows":
        import winreg
        ports = []
        for i in range(256):
            try:
                port = winreg.QueryValueEx(
                    winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'HARDWARE\\DEVICEMAP\\SERIALCOMM'),
                    f'\\Device\\Serial{i}'
                )[0]
                ports.append(port)
            except:
                pass
        return ports
    
    elif platform.system() == "Linux":
        import glob
        return glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
    
    elif platform.system() == "Darwin":  # macOS
        import glob
        return glob.glob('/dev/cu.usbmodem*') + glob.glob('/dev/cu.usbserial*')
    
    return []


def main():
    print("Serial Communication Test Utility")
    print("=" * 50)
    
    # List available ports
    ports = list_serial_ports()
    if ports:
        print(f"\nAvailable serial ports: {ports}")
    else:
        print("\nNo serial ports found!")
        sys.exit(1)
    
    # Ask user for port
    port = input(f"Enter serial port (default: {ports[0] if ports else 'COM3'}): ").strip()
    if not port:
        port = ports[0] if ports else 'COM3'
    
    # Ask for baud rate
    baudrate = input("Enter baud rate (default: 9600): ").strip()
    baudrate = int(baudrate) if baudrate else 9600
    
    # Test connection
    print(f"\nTesting connection to {port} at {baudrate} baud...")
    if not test_serial_connection(port, baudrate):
        print("[ERROR] Connection test failed")
        sys.exit(1)
    
    # Test commands
    response = input("\nTest keyboard commands? (y/n): ").strip().lower()
    if response == 'y':
        print("Connect microcontroller to work PC and press Enter...")
        input()
        test_keyboard_commands(port, baudrate)
    
    print("\nTest complete!")


if __name__ == '__main__':
    main()
