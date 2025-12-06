/*
  USB HID Keyboard Automation Firmware
  For Raspberry Pi Pico with RP2040 microcontroller
  Receives commands over serial (USB CDC) and executes keyboard actions
*/

#include <Keyboard.h>
#include <HID.h>

// Configuration
#define DEBUG_MODE true
#define BUFFER_SIZE 64
#define BAUD_RATE 9600

// Global variables
char commandBuffer[BUFFER_SIZE];
int bufferIndex = 0;

void setup() {
  // Initialize USB serial (CDC)
  Serial.begin(BAUD_RATE);
  Keyboard.begin();
  
  // Wait for serial to be ready (important for Pico)
  while (!Serial) {
    delay(10);
  }
  
  delay(1000);
  
  if (DEBUG_MODE) {
    Serial.println("Raspberry Pi Pico - USB HID Keyboard Ready");
    Serial.println("Waiting for commands...");
  }
}

void loop() {
  if (Serial.available() > 0) {
    char incomingByte = Serial.read();
    
    if (incomingByte == '\n') {
      commandBuffer[bufferIndex] = '\0';
      processCommand(commandBuffer);
      bufferIndex = 0;
    } else if (incomingByte == '\r') {
      // Ignore carriage return
    } else if (bufferIndex < BUFFER_SIZE - 1) {
      commandBuffer[bufferIndex++] = incomingByte;
    }
  }
}

void processCommand(const char* command) {
  if (DEBUG_MODE) {
    Serial.print("Command: ");
    Serial.println(command);
  }
  
  if (strncmp(command, "TYPE:", 5) == 0) {
    typeText(command + 5);
  } 
  else if (strncmp(command, "KEY:", 4) == 0) {
    pressKey(command + 4);
  }
  else if (strncmp(command, "COMBO:", 6) == 0) {
    pressCombo(command + 6);
  }
  else if (strncmp(command, "DELAY:", 6) == 0) {
    int delayMs = atoi(command + 6);
    delay(delayMs);
  }
  else if (strncmp(command, "PING", 4) == 0) {
    Serial.println("PONG");
  }
}

void typeText(const char* text) {
  for (int i = 0; text[i] != '\0'; i++) {
    Keyboard.press(text[i]);
    delay(50);
    Keyboard.release(text[i]);
    delay(50);
  }
}

void pressKey(const char* keyName) {
  char upperName[32];
  for (int i = 0; keyName[i] != '\0' && i < 31; i++) {
    upperName[i] = toupper(keyName[i]);
  }
  upperName[31] = '\0';
  
  uint8_t keyCode = 0;
  
  if (strcmp(upperName, "ENTER") == 0) {
    keyCode = KEY_RETURN;
  } 
  else if (strcmp(upperName, "BACKSPACE") == 0) {
    keyCode = KEY_BACKSPACE;
  }
  else if (strcmp(upperName, "DELETE") == 0) {
    keyCode = KEY_DELETE;
  }
  else if (strcmp(upperName, "TAB") == 0) {
    keyCode = KEY_TAB;
  }
  else if (strcmp(upperName, "ESCAPE") == 0) {
    keyCode = KEY_ESC;
  }
  else if (strcmp(upperName, "SPACE") == 0) {
    keyCode = ' ';
  }
  
  if (keyCode != 0) {
    Keyboard.press(keyCode);
    delay(100);
    Keyboard.releaseAll();
  }
}

void pressCombo(const char* combo) {
  boolean ctrlPressed = false;
  boolean shiftPressed = false;
  boolean altPressed = false;
  char finalKey = 0;
  
  char comboCopy[32];
  strncpy(comboCopy, combo, 31);
  comboCopy[31] = '\0';
  
  char* token = strtok(comboCopy, "+");
  while (token != NULL) {
    char upperToken[32];
    for (int i = 0; token[i] != '\0' && i < 31; i++) {
      upperToken[i] = toupper(token[i]);
    }
    upperToken[31] = '\0';
    
    if (strcmp(upperToken, "CTRL") == 0) {
      ctrlPressed = true;
    } 
    else if (strcmp(upperToken, "SHIFT") == 0) {
      shiftPressed = true;
    }
    else if (strcmp(upperToken, "ALT") == 0) {
      altPressed = true;
    }
    else {
      finalKey = upperToken[0];
    }
    
    token = strtok(NULL, "+");
  }
  
  if (ctrlPressed) Keyboard.press(KEY_LEFT_CTRL);
  if (shiftPressed) Keyboard.press(KEY_LEFT_SHIFT);
  if (altPressed) Keyboard.press(KEY_LEFT_ALT);
  
  if (finalKey != 0) {
    Keyboard.press(finalKey);
  }
  
  delay(100);
  Keyboard.releaseAll();
}
