/* Sweep
  by BARRAGAN <http://barraganstudio.com>
  This example code is in the public domain.

  modified 28 May 2015
  by Michael C. Miller
  modified 8 Nov 2013
  by Scott Fitzgerald

  http://arduino.cc/en/Tutorial/Sweep
*/

#include <Servo.h>
bool stop1 = false;
bool run1 = false;
int currentServo = 4;

// Servo classes to match Python structure
class ServoController {
  public:
    Servo servo;
    int pin;
    int currentAngle;
    int maxAngle;
    int minAngle;
    float delayTime;
    
  public:
    ServoController(int servoPin, int maxAng, int minAng, float del) {
      pin = servoPin;
      maxAngle = maxAng;
      minAngle = minAng;
      delayTime = del;
      currentAngle = minAng;
    }
    
    void attachServo() {
      servo.attach(pin);
    }
    
    void setAngle(int angle) {
      angle = constrain(angle, minAngle, maxAngle);
      currentAngle = angle;
      servo.write(angle);
    }
    
    int getAngle() {
      return currentAngle;
    }
    
    void moveServo(bool reverse) {
      int time_a;
      run1 = true;
      if (!reverse) {
        time_a = maxAngle - currentAngle;
      } else {
        time_a = currentAngle - minAngle;
      }
      
      for (int i = 0; i < time_a; i++) {
        if (stop1) {break;}
        if (reverse) {
          currentAngle -= 1;
        } else {
          currentAngle += 1;
        }
        setAngle(currentAngle);
        delay(delayTime * 1000); // Convert seconds to milliseconds
      }
      run1 = false;
    }
    
    void up() {
      moveServo(true);
    }
    
    void down() {
      moveServo(false);
    }
};

// Create servo objects
ServoController kleshnya(16, 150, 0, 0.08);
ServoController kist_rotary(5, 150, 0, 0.08);
ServoController kist_bend(4, 150, 0, 0.08);
ServoController shoulder(0, 150, 0, 0.08);
ServoController collarbone(14, 150, 0, 0.08);
ServoController guohu(12, 150, 0, 0.08);

// Create a list of servo {controllers
const int NUM_SERVOS = 6;
ServoController* servoList[NUM_SERVOS] = {&kleshnya, &kist_rotary, &kist_bend, &shoulder, &collarbone, &guohu};

void up (){
    for (auto obj: servoList){
        if (currentServo == obj->pin){
          obj->up();
       }
    }
  }
  
void setup() {
  // Attach all servos
  for (int i = 0; i < NUM_SERVOS; i++) {
    servoList[i]->attachServo();
  }
  
  // Initialize servos to minimum angle
  for (int i = 0; i < NUM_SERVOS; i++) {
    servoList[i]->setAngle(0);
  }
}

void loop() {
  up();
  delay(100);
}
