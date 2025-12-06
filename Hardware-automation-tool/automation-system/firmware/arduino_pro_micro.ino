/*
  USB HID Keyboard Automation Firmware
  For Arduino Pro Micro with USB HID capabilities
  Receives commands over serial and executes keyboard actions
*/

#include "Keyboard.h"

// Configuration
#define BAUD_RATE 9600
#define BUFFER_SIZE 64
#define DEBUG_MODE true

// Pin definitions
#define STATUS_LED 13

// Global variables
char commandBuffer[BUFFER_SIZE];
int bufferIndex = 0;

// Keyboard command mapping
void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(STATUS_LED, OUTPUT);
  Keyboard.begin();
  
  digitalWrite(STATUS_LED, LOW);
  delay(500);
  digitalWrite(STATUS_LED, HIGH);
  delay(500);
  digitalWrite(STATUS_LED, LOW);
  
  if (DEBUG_MODE) {
    Serial.println("Arduino Pro Micro - USB HID Keyboard Ready");
    Serial.println("Waiting for commands...");
  }
}

void loop() {
  // Check for incoming serial data
  if (Serial.available() > 0) {
    char incomingByte = Serial.read();
    
    // Build command string until newline
    if (incomingByte == '\n') {
      commandBuffer[bufferIndex] = '\0';
      processCommand(commandBuffer);
      bufferIndex = 0;
      digitalWrite(STATUS_LED, HIGH);
      delay(100);
      digitalWrite(STATUS_LED, LOW);
    } else if (incomingByte == '\r') {
      // Ignore carriage return
    } else if (bufferIndex < BUFFER_SIZE - 1) {
      commandBuffer[bufferIndex++] = incomingByte;
    }
  }
}

/*
  Process incoming commands
  Format: TYPE:text or KEY:keyname or COMBO:key1+key2
*/
void processCommand(const char* command) {
  if (DEBUG_MODE) {
    Serial.print("Received: ");
    Serial.println(command);
  }
  
  // Parse command type
  if (strncmp(command, "TYPE:", 5) == 0) {
    // Type text command
    const char* text = command + 5;
    typeText(text);
  } 
  else if (strncmp(command, "KEY:", 4) == 0) {
    // Single key command
    const char* keyName = command + 4;
    pressKey(keyName);
  }
  else if (strncmp(command, "COMBO:", 6) == 0) {
    // Key combination command
    const char* combo = command + 6;
    pressCombo(combo);
  }
  else if (strncmp(command, "DELAY:", 6) == 0) {
    // Delay command
    int delayMs = atoi(command + 6);
    delay(delayMs);
  }
  else if (strncmp(command, "PING", 4) == 0) {
    // Heartbeat/ping command
    Serial.println("PONG");
  }
  else {
    if (DEBUG_MODE) {
      Serial.println("Unknown command");
    }
  }
}

/*
  Type a string of text
*/
void typeText(const char* text) {
  for (int i = 0; text[i] != '\0'; i++) {
    Keyboard.press(text[i]);
    delay(50);
    Keyboard.release(text[i]);
    delay(50);
  }
  
  if (DEBUG_MODE) {
    Serial.print("Typed: ");
    Serial.println(text);
  }
}

/*
  Press a single key by name
  Common keys: ENTER, BACKSPACE, DELETE, ESCAPE, HOME, END, etc.
*/
void pressKey(const char* keyName) {
  // Convert to uppercase for comparison
  char upperName[32];
  for (int i = 0; keyName[i] != '\0' && i < 31; i++) {
    upperName[i] = toupper(keyName[i]);
  }
  upperName[31] = '\0';
  
  uint8_t keyCode = 0;
  
  if (strcmp(upperName, "ENTER") == 0 || strcmp(upperName, "RETURN") == 0) {
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
  else if (strcmp(upperName, "HOME") == 0) {
    keyCode = KEY_HOME;
  }
  else if (strcmp(upperName, "END") == 0) {
    keyCode = KEY_END;
  }
  else if (strcmp(upperName, "PAGE_UP") == 0) {
    keyCode = KEY_PAGE_UP;
  }
  else if (strcmp(upperName, "PAGE_DOWN") == 0) {
    keyCode = KEY_PAGE_DOWN;
  }
  else if (strcmp(upperName, "UP") == 0) {
    keyCode = KEY_UP_ARROW;
  }
  else if (strcmp(upperName, "DOWN") == 0) {
    keyCode = KEY_DOWN_ARROW;
  }
  else if (strcmp(upperName, "LEFT") == 0) {
    keyCode = KEY_LEFT_ARROW;
  }
  else if (strcmp(upperName, "RIGHT") == 0) {
    keyCode = KEY_RIGHT_ARROW;
  }
  else if (strcmp(upperName, "SPACE") == 0) {
    keyCode = ' ';
  }
  
  if (keyCode != 0) {
    Keyboard.press(keyCode);
    delay(100);
    Keyboard.releaseAll();
    
    if (DEBUG_MODE) {
      Serial.print("Key pressed: ");
      Serial.println(keyName);
    }
  } else if (DEBUG_MODE) {
    Serial.print("Unknown key: ");
    Serial.println(keyName);
  }
}

/*
  Press key combinations (e.g., CTRL+C, ALT+F4)
*/
void pressCombo(const char* combo) {
  // Parse format: CTRL+C or SHIFT+ALT+DEL
  boolean ctrlPressed = false;
  boolean shiftPressed = false;
  boolean altPressed = false;
  char finalKey = 0;
  
  char comboCopy[32];
  strncpy(comboCopy, combo, 31);
  comboCopy[31] = '\0';
  
  // Parse modifiers
  char* token = strtok(comboCopy, "+");
  while (token != NULL) {
    char upperToken[32];
    for (int i = 0; token[i] != '\0' && i < 31; i++) {
      upperToken[i] = toupper(token[i]);
    }
    upperToken[31] = '\0';
    
    if (strcmp(upperToken, "CTRL") == 0 || strcmp(upperToken, "CONTROL") == 0) {
      ctrlPressed = true;
    } 
    else if (strcmp(upperToken, "SHIFT") == 0) {
      shiftPressed = true;
    }
    else if (strcmp(upperToken, "ALT") == 0) {
      altPressed = true;
    }
    else {
      // This is the final key
      finalKey = upperToken[0];
    }
    
    token = strtok(NULL, "+");
  }
  
  // Execute combination
  if (ctrlPressed) Keyboard.press(KEY_LEFT_CTRL);
  if (shiftPressed) Keyboard.press(KEY_LEFT_SHIFT);
  if (altPressed) Keyboard.press(KEY_LEFT_ALT);
  
  if (finalKey != 0) {
    Keyboard.press(finalKey);
  }
  
  delay(100);
  Keyboard.releaseAll();
  
  if (DEBUG_MODE) {
    Serial.print("Combo pressed: ");
    Serial.println(combo);
  }
}
