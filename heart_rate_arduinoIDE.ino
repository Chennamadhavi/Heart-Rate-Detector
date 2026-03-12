#include <Arduino.h>
#include <math.h>

// Pin setup
const int sensorPin = A0;    // Pulse sensor or potentiometer input
const int redLED = 13;       // Abnormal
const int greenLED = 12;     // Normal
const int blueLED = 11;      // Low

int sensorValue = 0;
float normalized = 0.0;
float heartRate = 0.0;
int prediction = 0;

unsigned long lastUpdate = 0;
const unsigned long updateInterval = 500; // Update twice per second

void setup() {
  Serial.begin(9600);   // Communicate with COMPIM
  pinMode(redLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  pinMode(blueLED, OUTPUT);
  Serial.println("System Ready...");
}

void loop() {
  // Use millis() instead of delay() to keep simulation responsive
  unsigned long currentMillis = millis();
  if (currentMillis - lastUpdate >= updateInterval) {
    lastUpdate = currentMillis;

    // Read analog input (0–1023)
    sensorValue = analogRead(sensorPin);

    // Simulate heart rate (50–120 BPM)
    heartRate = map(sensorValue, 0, 1023, 50, 120);

    // Normalize (0–1)
    normalized = sensorValue / 1023.0;

    // --- Simple ML-like Logic ---
    if (normalized < 0.3) {
      prediction = 0;  // Low
    } else if (normalized < 0.7) {
      prediction = 1;  // Normal
    } else {
      prediction = 2;  // High/Abnormal
    }

    // --- LED Indications ---
    digitalWrite(redLED, prediction == 2);
    digitalWrite(greenLED, prediction == 1);
    digitalWrite(blueLED, prediction == 0);

    // --- Serial Output (limited frequency) ---
    Serial.print("Heart Rate: ");
    Serial.print(heartRate);
    Serial.print(" | Prediction: ");
    if (prediction == 0) Serial.println("LOW");
    else if (prediction == 1) Serial.println("NORMAL");
    else Serial.println("HIGH/ABNORMAL");

    // Only numeric heart rate for Python ML input
    Serial.println(heartRate);
  }
}
