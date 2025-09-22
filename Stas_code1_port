#include <Servo.h>

class MyServo {
  public:
    Servo servo;
    int angle;
    int max_angle;
    int min_angle;
    int pin;
    int delay_ms;

    MyServo(int p, int min_a, int max_a, int d) {
      pin = p;
      min_angle = min_a;
      max_angle = max_a;
      delay_ms = d;
      angle = min_angle;
    }

    void attach() {
      servo.attach(pin);
      servo.write(angle);
    }

    void set_angle(int a) {
      angle = constrain(a, min_angle, max_angle);
      servo.write(angle);
    }

    void movement(bool reverse) {
      int time_a;
      if (!reverse) {
        time_a = max_angle - angle;
      } else {
        time_a = angle - min_angle;
      }
      for (int i = 0; i < time_a; i++) {
        if (!reverse) {
          angle++;
        } else {
          angle--;
        }
        set_angle(angle);
        delay(delay_ms);
      }
    }

    void up() {
      movement(true);
    }

    void down() {
      movement(false);
    }
};

// !create a list of classes and insert all existing classes into it!
MyServo kleshnya(16, 0, 150, 80);
MyServo kist_rotary(5, 0, 150, 80);
MyServo kist_bend(4, 0, 150, 80);
MyServo shoulder(0, 0, 150, 80);
MyServo collarbone(14, 0, 150, 80);
MyServo guohu(12, 0, 150, 80);

MyServo* classList[] = {&kleshnya, &kist_rotary, &kist_bend, &shoulder, &collarbone, &guohu};

void setup() {
  for (int i = 0; i < sizeof(classList) / sizeof(classList[0]); i++) {
    classList[i]->attach();
  }
}

void loop() {
  // Example: move kleshnya up
  kleshnya.up();
  delay(1000);
  kleshnya.down();
  delay(1000);
}
