#include <Servo.h>
bool run1 = false;
bool stop1 = false;

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

    void attach1() {
      servo.attach(pin);
      servo.write(angle);
    }

    void set_angle(int a) {
      angle = constrain(a, min_angle, max_angle);
      servo.write(angle);
    }

    void movement(bool reverse) {
      int time_a;
      run1 = true;
      if (!reverse) {
        time_a = max_angle - angle;
      } else {
        time_a = angle - min_angle;
      }
      for (int i = 0; i < time_a; i++) {
        if (stop1) {break;}
        if (!reverse) {
          angle++;
        } else {
          angle--;
        }
        set_angle(angle);
        Serial.println(angle);
        delay(delay_ms);
      }
      run1 = false;
    }

    void up() {
      movement(true);
    }

    void down() {
      movement(false);
    }
};

// !create a list of classes and insert all existing classes into it!
MyServo kleshnya(16, 0, 160, 30); //Стискати кулак
MyServo kist_rotary(5, 0, 150, 30); //Крутить кулачок
MyServo kist_bend(4, 0, 100, 30); //2 изгиб локтя
MyServo shoulder(0, 110, 180, 30); //Локоть
MyServo collarbone(14, 0, 180, 30); //Основание

MyServo guohu(12, 0, 90, 30);

MyServo* classList[] = {&kleshnya, &kist_rotary, &kist_bend, &shoulder, &collarbone, &guohu};
void (*softReset) (void) = 0;

void setup() {
  for (int i = 0; i < sizeof(classList) / sizeof(classList[0]); i++) {
    classList[i]->attach1();
    Serial.begin(9600);
  }
  shoulder.set_angle(0);
  kist_bend.set_angle(0);
  kleshnya.set_angle(0);
  guohu.set_angle(0);
}

String text = "";
void loop() {
  if (Serial.available()){
     text = Serial.readString();
     text.trim();
     text.toLowerCase();
     Serial.print("Reading: ");
     Serial.println(text);
   }

  if (text == "up") {
         guohu.down();
         shoulder.down();
         kist_bend.down();
   }

  else if (text == "down"){
    guohu.up();
    shoulder.up();
    kist_bend.up();
  }
}
