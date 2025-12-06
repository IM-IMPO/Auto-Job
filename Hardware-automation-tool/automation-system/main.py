#!/usr/bin/env python3
"""
Hardware-Assisted Automation System
Main entry point for screen capture, OCR processing, and command execution.
Captures HDMI input, analyzes content, and sends commands to USB microcontroller.
"""

import cv2
import numpy as np
import pytesseract
import json
import serial
import time
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CaptureSource(Enum):
    HDMI_CARD = 0  # Default video device for HDMI capture card
    WEBCAM = 1
    TEST_IMAGE = 2


@dataclass
class TriggerMatch:
    trigger_name: str
    command: str
    confidence: float
    region: Tuple[int, int, int, int]


class ConfigManager:
    """Loads and manages automation configuration from JSON."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {self.config_path}")
            sys.exit(1)
    
    def get_triggers(self) -> List[Dict]:
        return self.config.get('triggers', [])
    
    def get_ocr_regions(self) -> Dict:
        return self.config.get('ocr_regions', {})
    
    def get_command_mapping(self) -> Dict:
        return self.config.get('command_mapping', {})
    
    def get_threshold(self) -> float:
        return self.config.get('ocr_threshold', 0.7)


class ImageProcessor:
    """Handles image preprocessing for better OCR accuracy."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Apply preprocessing to improve OCR accuracy."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply thresholding
        _, binary = cv2.threshold(enhanced, 150, 255, cv2.THRESH_BINARY)
        
        # Denoise
        denoised = cv2.medianBlur(binary, 3)
        
        if self.debug:
            logger.debug("Image preprocessing applied")
        
        return denoised
    
    def crop_region(self, frame: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
        """Crop a specific region from frame (x1, y1, x2, y2)."""
        x1, y1, x2, y2 = region
        return frame[y1:y2, x1:x2]


class OCREngine:
    """Handles OCR text recognition using Tesseract."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.image_processor = ImageProcessor(debug)
        self._verify_tesseract()
    
    def _verify_tesseract(self):
        """Verify Tesseract is installed and accessible."""
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR engine verified")
        except pytesseract.TesseractNotFoundError:
            logger.error(
                "Tesseract not found. Install with:\n"
                "  Windows: choco install tesseract\n"
                "  Linux: sudo apt install tesseract-ocr\n"
                "  macOS: brew install tesseract"
            )
            sys.exit(1)
    
    def extract_text(self, frame: np.ndarray, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """Extract text from frame using OCR."""
        if region:
            frame = self.image_processor.crop_region(frame, region)
        
        processed = self.image_processor.preprocess(frame)
        text = pytesseract.image_to_string(processed)
        
        if self.debug:
            logger.debug(f"OCR extracted: {text[:100]}...")
        
        return text.strip()
    
    def find_text_regions(self, frame: np.ndarray) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """Find all text regions in frame with bounding boxes."""
        processed = self.image_processor.preprocess(frame)
        data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
        
        regions = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if text and float(data['conf'][i]) > 50:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                regions.append((text, (x, y, x + w, y + h)))
        
        return regions


class ScreenCapture:
    """Handles screen/video capture from HDMI card or other sources."""
    
    def __init__(self, source: CaptureSource = CaptureSource.HDMI_CARD):
        self.source = source
        self.cap = None
        self.initialize()
    
    def initialize(self):
        """Initialize video capture."""
        if self.source == CaptureSource.HDMI_CARD:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            logger.info("HDMI capture card initialized")
        elif self.source == CaptureSource.WEBCAM:
            self.cap = cv2.VideoCapture(0)
            logger.info("Webcam initialized")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Capture and return a frame."""
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            logger.error("Failed to capture frame")
            return None
        
        return frame
    
    def release(self):
        """Release capture resources."""
        if self.cap:
            self.cap.release()


class TriggerMatcher:
    """Matches OCR text against configured triggers."""
    
    def __init__(self, triggers: List[Dict], threshold: float = 0.7):
        self.triggers = triggers
        self.threshold = threshold
    
    def match(self, text: str) -> List[TriggerMatch]:
        """Find matching triggers in text."""
        matches = []
        text_lower = text.lower()
        
        for trigger in self.triggers:
            keywords = trigger.get('keywords', [])
            command = trigger.get('command', '')
            name = trigger.get('name', '')
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    confidence = 1.0 if keyword.lower() == text_lower else 0.8
                    matches.append(TriggerMatch(
                        trigger_name=name,
                        command=command,
                        confidence=confidence,
                        region=(0, 0, 0, 0)
                    ))
        
        return matches


class SerialCommandExecutor:
    """Handles serial communication with USB microcontroller."""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.connect()
    
    def connect(self):
        """Establish serial connection."""
        try:
            self.serial_conn = serial.Serial(
                self.port,
                self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # Wait for microcontroller to initialize
            logger.info(f"Serial connection established on {self.port}")
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            raise
    
    def send_command(self, command: str) -> bool:
        """Send command to microcontroller."""
        if self.serial_conn is None or not self.serial_conn.is_open:
            logger.error("Serial connection not open")
            return False
        
        try:
            self.serial_conn.write(f"{command}\n".encode('utf-8'))
            logger.info(f"Command sent: {command}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to send command: {e}")
            return False
    
    def read_response(self) -> Optional[str]:
        """Read response from microcontroller."""
        if self.serial_conn is None or not self.serial_conn.is_open:
            return None
        
        if self.serial_conn.in_waiting > 0:
            response = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
            return response
        
        return None
    
    def close(self):
        """Close serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logger.info("Serial connection closed")


class AutomationEngine:
    """Main automation engine orchestrating all components."""
    
    def __init__(self, config_path: str, serial_port: str, debug: bool = False):
        self.debug = debug
        self.config_manager = ConfigManager(config_path)
        self.ocr_engine = OCREngine(debug)
        self.image_processor = ImageProcessor(debug)
        self.screen_capture = ScreenCapture()
        self.trigger_matcher = TriggerMatcher(
            self.config_manager.get_triggers(),
            self.config_manager.get_threshold()
        )
        self.command_executor = SerialCommandExecutor(serial_port)
        self.mapping = self.config_manager.get_command_mapping()
    
    def process_frame(self) -> List[TriggerMatch]:
        """Capture and process a single frame."""
        frame = self.screen_capture.get_frame()
        if frame is None:
            return []
        
        # Extract text from regions of interest
        ocr_regions = self.config_manager.get_ocr_regions()
        all_text = ""
        
        for region_name, region_coords in ocr_regions.items():
            text = self.ocr_engine.extract_text(frame, tuple(region_coords))
            if text:
                all_text += f" {text}"
                if self.debug:
                    logger.debug(f"Region '{region_name}': {text}")
        
        # Find matching triggers
        matches = self.trigger_matcher.match(all_text)
        
        return matches
    
    def execute_matches(self, matches: List[TriggerMatch]):
        """Execute commands for matched triggers."""
        for match in matches:
            # Get keystroke sequence from mapping
            keystrokes = self.mapping.get(match.command, [])
            
            if keystrokes:
                # Send each keystroke command to microcontroller
                for keystroke_cmd in keystrokes:
                    self.command_executor.send_command(keystroke_cmd)
                    time.sleep(0.1)  # Small delay between commands
                
                logger.info(f"Executed: {match.trigger_name} -> {match.command}")
    
    def run_continuous(self, interval: float = 1.0):
        """Run automation in continuous mode."""
        logger.info("Starting continuous automation mode")
        
        try:
            while True:
                matches = self.process_frame()
                
                if matches:
                    logger.info(f"Found {len(matches)} trigger matches")
                    self.execute_matches(matches)
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("Automation stopped by user")
        finally:
            self.shutdown()
    
    def run_test(self, test_image_path: str):
        """Run automation on a static test image."""
        logger.info(f"Running test mode with image: {test_image_path}")
        
        frame = cv2.imread(test_image_path)
        if frame is None:
            logger.error(f"Failed to load test image: {test_image_path}")
            return
        
        # Process test image
        text = self.ocr_engine.extract_text(frame)
        logger.info(f"OCR Result: {text}")
        
        matches = self.trigger_matcher.match(text)
        logger.info(f"Trigger Matches: {[m.trigger_name for m in matches]}")
        
        self.execute_matches(matches)
    
    def shutdown(self):
        """Clean up resources."""
        logger.info("Shutting down automation engine")
        self.screen_capture.release()
        self.command_executor.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Hardware-Assisted Automation System'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--port',
        required=True,
        help='Serial port for microcontroller (e.g., COM3, /dev/ttyACM0)'
    )
    parser.add_argument(
        '--test',
        help='Run test mode with static image'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=1.0,
        help='Processing interval in seconds'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    engine = AutomationEngine(
        config_path=args.config,
        serial_port=args.port,
        debug=args.debug
    )
    
    if args.test:
        engine.run_test(args.test)
    else:
        engine.run_continuous(interval=args.interval)


if __name__ == '__main__':
    main()
