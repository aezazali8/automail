#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

const int servoPins[5] = {11, 12, 13, 14, 15};  // Thumb, Index, Middle, Ring, Pinky
const int SERVOMIN = 102;
const int SERVOMAX = 512;

String input = "";

uint16_t angleToPulse(float angle) {
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

void setup() {
  Serial.begin(115200);
  pwm.begin();
  pwm.setPWMFreq(50);
  delay(10);
}

void loop() {
  while (Serial.available()) {//this cod gets the finger positions from opencv
    char c = Serial.read();
    if (c == '\n') {
      int angles[5];
      int i = 0;
      char *token = strtok((char*)input.c_str(), ",");
      while (token != NULL && i < 5) {
        angles[i++] = atoi(token);
        token = strtok(NULL, ",");
      }
      input = "";

      if (i == 5) {
        for (int j = 0; j < 5; j++) {
          pwm.setPWM(servoPins[j], 0, angleToPulse(angles[j]));
        }
      }
    } else {
      input += c;
    }
  }
}

